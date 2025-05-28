"""
Hydraulic Systems Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for the Condition Monitoring
of Hydraulic Systems dataset, supporting MCP/A2A integration for industrial monitoring.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from sklearn.preprocessing import StandardScaler

from .dataset_connector_base import DatasetConnectorBase

logger = logging.getLogger(__name__)

class HydraulicSystemsDatasetConnector(DatasetConnectorBase):
    """
    Connector for Condition Monitoring of Hydraulic Systems Dataset.
    
    This connector provides protocol-native ingestion, validation, and
    transformation for the Hydraulic Systems dataset, with support
    for condition monitoring and predictive maintenance use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "hydraulic-systems-connector",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the Hydraulic Systems dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "hydraulic", "condition_monitoring"],
            "sensor_files": {
                "PS1": "PS1.txt",
                "PS2": "PS2.txt",
                "PS3": "PS3.txt",
                "PS4": "PS4.txt",
                "PS5": "PS5.txt",
                "PS6": "PS6.txt",
                "FS1": "FS1.txt",
                "FS2": "FS2.txt",
                "TS1": "TS1.txt",
                "TS2": "TS2.txt",
                "TS3": "TS3.txt",
                "TS4": "TS4.txt",
                "VS1": "VS1.txt",
                "CE": "CE.txt",
                "CP": "CP.txt",
                "SE": "SE.txt"
            },
            "target_files": {
                "cooler": "profile.txt",
                "valve": "profile.txt",
                "pump": "profile.txt",
                "accumulator": "profile.txt"
            },
            "sensor_descriptions": {
                "PS1": "Pressure sensor 1 (bar)",
                "PS2": "Pressure sensor 2 (bar)",
                "PS3": "Pressure sensor 3 (bar)",
                "PS4": "Pressure sensor 4 (bar)",
                "PS5": "Pressure sensor 5 (bar)",
                "PS6": "Pressure sensor 6 (bar)",
                "FS1": "Flow sensor 1 (l/min)",
                "FS2": "Flow sensor 2 (l/min)",
                "TS1": "Temperature sensor 1 (°C)",
                "TS2": "Temperature sensor 2 (°C)",
                "TS3": "Temperature sensor 3 (°C)",
                "TS4": "Temperature sensor 4 (°C)",
                "VS1": "Vibration sensor 1 (mm/s)",
                "CE": "Cooling efficiency (%)",
                "CP": "Cooling power (kW)",
                "SE": "System efficiency (%)"
            },
            "target_descriptions": {
                "cooler": "Cooler condition (3: close to total failure, 20: reduced efficiency, 100: full efficiency)",
                "valve": "Valve condition (100: optimal switching behavior, 90: small lag, 80: severe lag, 73: close to total failure)",
                "pump": "Internal pump leakage (0: no leakage, 1: weak leakage, 2: severe leakage)",
                "accumulator": "Hydraulic accumulator (130: optimal pressure, 115: slightly reduced pressure, 100: severely reduced pressure, 90: close to total failure)"
            },
            "target_columns": {
                "cooler_condition": 0,
                "valve_condition": 1,
                "pump_leakage": 2,
                "accumulator_pressure": 3
            },
            "target_mappings": {
                "cooler_condition": {
                    3: "close_to_failure",
                    20: "reduced_efficiency",
                    100: "full_efficiency"
                },
                "valve_condition": {
                    100: "optimal",
                    90: "small_lag",
                    80: "severe_lag",
                    73: "close_to_failure"
                },
                "pump_leakage": {
                    0: "no_leakage",
                    1: "weak_leakage",
                    2: "severe_leakage"
                },
                "accumulator_pressure": {
                    130: "optimal",
                    115: "slightly_reduced",
                    100: "severely_reduced",
                    90: "close_to_failure"
                }
            }
        }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name="hydraulic_systems",
            dataset_type="timeseries",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.sensors_dir = os.path.join(self.processed_dir, "sensors")
        self.targets_dir = os.path.join(self.processed_dir, "targets")
        self.merged_dir = os.path.join(self.processed_dir, "merged")
        self.models_dir = os.path.join(self.processed_dir, "models")
        
        os.makedirs(self.sensors_dir, exist_ok=True)
        os.makedirs(self.targets_dir, exist_ok=True)
        os.makedirs(self.merged_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("Initialized Hydraulic Systems dataset connector")
    
    def ingest_dataset(
        self,
        data_dir: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the complete Hydraulic Systems dataset.
        
        Args:
            data_dir: Directory containing the dataset files
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
                        "status": "dataset_ingestion_started",
                        "dataset": self.dataset_name,
                        "data_dir": data_dir
                    }
                )
            
            # Ingest sensor data
            sensor_results = {}
            for sensor_name, sensor_file in self.config["sensor_files"].items():
                file_path = os.path.join(data_dir, sensor_file)
                if os.path.exists(file_path):
                    sensor_results[sensor_name] = self.ingest_data(
                        source_path=file_path,
                        validate=validate,
                        transform=False,  # We'll transform after merging
                        emit_events=False,
                        metadata={"sensor_name": sensor_name}
                    )
                else:
                    logger.warning(f"Sensor file not found: {file_path}")
            
            # Ingest target data
            target_results = {}
            for target_name, target_file in self.config["target_files"].items():
                file_path = os.path.join(data_dir, target_file)
                if os.path.exists(file_path):
                    target_results[target_name] = self.ingest_data(
                        source_path=file_path,
                        validate=validate,
                        transform=False,  # We'll transform after merging
                        emit_events=False,
                        metadata={"target_name": target_name}
                    )
                else:
                    logger.warning(f"Target file not found: {file_path}")
            
            # Process the complete dataset
            if sensor_results and target_results:
                merged_result = self._process_complete_dataset(
                    sensor_results=sensor_results,
                    target_results=target_results,
                    transform=transform
                )
            else:
                merged_result = {
                    "success": False,
                    "error": "Failed to ingest sensor or target data"
                }
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "success": merged_result["success"],
                "status": "dataset_ingestion_completed" if merged_result["success"] else "dataset_ingestion_failed",
                "components": {
                    "sensors": sensor_results,
                    "targets": target_results,
                    "merged": merged_result
                },
                "statistics": self.metadata["statistics"] if "statistics" in self.metadata else {},
                "duration": duration
            }
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_ingestion_completed" if result["success"] else "dataset_ingestion_failed",
                        "dataset": self.dataset_name,
                        "statistics": self.metadata["statistics"] if "statistics" in self.metadata else {},
                        "duration": duration
                    }
                )
            
            logger.info(f"Completed dataset ingestion for {self.dataset_name} in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Failed to ingest dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_ingestion_failed",
                        "dataset": self.dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "status": "dataset_ingestion_failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def _load_data(self, source_path: str, metadata: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Load data from source path.
        
        Args:
            source_path: Path to the source data
            metadata: Optional metadata about the data being loaded
            
        Returns:
            Loaded data as DataFrame
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Determine file type and load accordingly
        if source_path.endswith('.txt'):
            # The dataset uses space-delimited text files
            df = pd.read_csv(source_path, header=None, delim_whitespace=True)
            
            # Handle specific file types
            if metadata and "sensor_name" in metadata:
                sensor_name = metadata["sensor_name"]
                # Each sensor file has a column for each cycle
                df.columns = [f"{sensor_name}_cycle_{i+1}" for i in range(len(df.columns))]
            elif metadata and "target_name" in metadata:
                # The profile.txt file contains target variables
                # We need to extract the specific target column based on config
                target_name = metadata["target_name"]
                target_col = self.config["target_columns"].get(f"{target_name}_condition", 0)
                
                if target_col < len(df.columns):
                    # Extract just the target column
                    df = df.iloc[:, [target_col]]
                    df.columns = [target_name]
                else:
                    logger.warning(f"Target column {target_col} out of range for {target_name}")
        elif source_path.endswith('.csv'):
            df = pd.read_csv(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        return df
    
    def _validate_data(self, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate the Hydraulic Systems dataset.
        
        Args:
            data: Data to validate
            metadata: Optional metadata about the data being validated
            
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check if data is empty
        if data.empty:
            errors.append("DataFrame is empty")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }
        
        # Check for numeric data types
        non_numeric_cols = []
        for col in data.columns:
            if not pd.api.types.is_numeric_dtype(data[col]):
                non_numeric_cols.append(col)
        
        if non_numeric_cols:
            errors.append(f"Non-numeric columns found: {non_numeric_cols}")
        
        # Check for missing values
        missing_count = data.isna().sum().sum()
        if missing_count > 0:
            warnings.append(f"Data contains {missing_count} missing values")
        
        # Specific validations based on data type
        if metadata and "sensor_name" in metadata:
            sensor_name = metadata["sensor_name"]
            
            # Check expected value ranges for specific sensors
            if sensor_name.startswith("PS"):  # Pressure sensors
                if (data < 0).any().any():
                    warnings.append(f"Negative pressure values found in {sensor_name}")
                
                if (data > 200).any().any():  # Assuming max pressure is 200 bar
                    warnings.append(f"Unusually high pressure values found in {sensor_name}")
            
            elif sensor_name.startswith("TS"):  # Temperature sensors
                if (data < -20).any().any():
                    warnings.append(f"Unusually low temperature values found in {sensor_name}")
                
                if (data > 100).any().any():  # Assuming max temperature is 100°C
                    warnings.append(f"Unusually high temperature values found in {sensor_name}")
            
            elif sensor_name.startswith("FS"):  # Flow sensors
                if (data < 0).any().any():
                    warnings.append(f"Negative flow values found in {sensor_name}")
        
        elif metadata and "target_name" in metadata:
            target_name = metadata["target_name"]
            
            # Check if target values match expected values
            if target_name in self.config["target_mappings"]:
                expected_values = list(self.config["target_mappings"][target_name].keys())
                actual_values = data[target_name].unique()
                
                unexpected_values = [val for val in actual_values if val not in expected_values]
                if unexpected_values:
                    warnings.append(f"Unexpected values found in {target_name}: {unexpected_values}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _process_complete_dataset(
        self,
        sensor_results: Dict[str, Dict[str, Any]],
        target_results: Dict[str, Dict[str, Any]],
        transform: bool = True
    ) -> Dict[str, Any]:
        """
        Process the complete dataset after individual files are ingested.
        
        Args:
            sensor_results: Results from sensor data ingestion
            target_results: Results from target data ingestion
            transform: Whether to transform the data
            
        Returns:
            Processing result information
        """
        try:
            # Load raw sensor data
            sensor_dfs = {}
            for sensor_name, result in sensor_results.items():
                if result["success"] and "raw_path" in result:
                    sensor_dfs[sensor_name] = pd.read_csv(result["raw_path"])
            
            # Load raw target data
            target_dfs = {}
            for target_name, result in target_results.items():
                if result["success"] and "raw_path" in result:
                    target_dfs[target_name] = pd.read_csv(result["raw_path"])
            
            # Transpose sensor data to have cycles as rows and sensors as columns
            # This is needed because the original data has sensors as rows and cycles as columns
            transposed_sensors = {}
            for sensor_name, df in sensor_dfs.items():
                # Get the number of cycles
                n_cycles = len(df.columns)
                
                # Create a new dataframe with cycles as rows
                transposed_df = pd.DataFrame(index=range(n_cycles))
                
                # For each cycle, extract the sensor values
                for i in range(n_cycles):
                    col_name = f"{sensor_name}_cycle_{i+1}"
                    if col_name in df.columns:
                        # Extract the sensor values for this cycle
                        transposed_df[sensor_name] = df[col_name].values
                
                transposed_sensors[sensor_name] = transposed_df
            
            # Merge all sensor data
            if transposed_sensors:
                merged_sensors = pd.concat(transposed_sensors.values(), axis=1)
                
                # Add cycle_id column
                merged_sensors['cycle_id'] = range(1, len(merged_sensors) + 1)
                
                # Save merged sensor data
                merged_sensors_path = os.path.join(self.sensors_dir, "merged_sensors.csv")
                merged_sensors.to_csv(merged_sensors_path, index=False)
            else:
                return {
                    "success": False,
                    "error": "No sensor data to merge"
                }
            
            # Merge target data
            if target_dfs:
                # Create a dataframe with one row per cycle
                n_cycles = len(merged_sensors)
                merged_targets = pd.DataFrame(index=range(n_cycles))
                
                # Add each target variable
                for target_name, df in target_dfs.items():
                    if target_name in df.columns:
                        # Extract the target values
                        merged_targets[target_name] = df[target_name].values
                
                # Add cycle_id column
                merged_targets['cycle_id'] = range(1, len(merged_targets) + 1)
                
                # Save merged target data
                merged_targets_path = os.path.join(self.targets_dir, "merged_targets.csv")
                merged_targets.to_csv(merged_targets_path, index=False)
            else:
                return {
                    "success": False,
                    "error": "No target data to merge"
                }
            
            # Merge sensors and targets
            merged_df = pd.merge(merged_sensors, merged_targets, on='cycle_id')
            
            # Save merged raw data
            merged_raw_path = os.path.join(self.merged_dir, "hydraulic_systems_raw.csv")
            merged_df.to_csv(merged_raw_path, index=False)
            
            # Transform data if requested
            if transform:
                transformed_df = self._transform_data(merged_df)
                
                # Save transformed data
                transformed_path = os.path.join(self.merged_dir, "hydraulic_systems_transformed.csv")
                transformed_df.to_csv(transformed_path, index=False)
                
                # Update statistics and schema
                self._update_statistics(merged_df, transformed_df)
                self._update_schema(transformed_df)
                
                # Create dataset summary
                summary = self._create_dataset_summary(transformed_df)
                
                # Save summary
                summary_path = os.path.join(self.metadata_dir, "dataset_summary.json")
                with open(summary_path, 'w') as f:
                    json.dump(summary, f, indent=2)
                
                # Update metadata with summary
                self.metadata["dataset_summary"] = summary
                self._save_metadata()
                
                logger.info(f"Processed and transformed complete dataset, saved to {transformed_path}")
                
                return {
                    "success": True,
                    "merged_raw_path": merged_raw_path,
                    "transformed_path": transformed_path,
                    "summary_path": summary_path
                }
            else:
                # Update statistics and schema without transformation
                self._update_statistics(merged_df, merged_df)
                self._update_schema(merged_df)
                
                logger.info(f"Processed complete dataset without transformation, saved to {merged_raw_path}")
                
                return {
                    "success": True,
                    "merged_raw_path": merged_raw_path
                }
        except Exception as e:
            logger.error(f"Failed to process complete dataset: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the Hydraulic Systems dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Get sensor and target columns
        sensor_cols = [col for col in df.columns if col in self.config["sensor_descriptions"]]
        target_cols = [col for col in df.columns if col in self.config["target_mappings"]]
        
        # Handle missing values in sensor columns
        for col in sensor_cols:
            if df[col].isna().any():
                # Fill missing values with median
                df[col] = df[col].fillna(df[col].median())
        
        # Standardize sensor features
        scaler = StandardScaler()
        df[sensor_cols] = scaler.fit_transform(df[sensor_cols])
        
        # Save the scaler for later use
        import pickle
        scaler_path = os.path.join(self.models_dir, "sensor_scaler.pkl")
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        # Add categorical versions of target variables
        for target in target_cols:
            if target in self.config["target_mappings"]:
                mapping = self.config["target_mappings"][target]
                df[f"{target}_category"] = df[target].map(mapping)
        
        # Calculate rolling statistics for sensor data
        window_sizes = [3, 5, 10]
        
        for sensor in sensor_cols:
            for window in window_sizes:
                # Calculate rolling mean
                df[f"{sensor}_rolling_mean_{window}"] = df[sensor].rolling(window=window, min_periods=1).mean()
                
                # Calculate rolling standard deviation
                df[f"{sensor}_rolling_std_{window}"] = df[sensor].rolling(window=window, min_periods=1).std()
        
        # Calculate correlations between sensors
        corr_matrix = df[sensor_cols].corr()
        
        # Save correlation matrix
        corr_path = os.path.join(self.metadata_dir, "sensor_correlations.csv")
        corr_matrix.to_csv(corr_path)
        
        # Add binary indicators for critical conditions
        if "cooler" in target_cols:
            df["cooler_critical"] = (df["cooler"] == 3).astype(int)
        
        if "valve" in target_cols:
            df["valve_critical"] = (df["valve"] == 73).astype(int)
        
        if "pump" in target_cols:
            df["pump_critical"] = (df["pump"] == 2).astype(int)
        
        if "accumulator" in target_cols:
            df["accumulator_critical"] = (df["accumulator"] == 90).astype(int)
        
        # Add overall system health indicator
        critical_cols = [col for col in df.columns if col.endswith("_critical")]
        if critical_cols:
            df["system_health"] = 100 - (df[critical_cols].sum(axis=1) * 25)
        
        return df
    
    def _create_dataset_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create a summary of the dataset.
        
        Args:
            data: Processed dataset
            
        Returns:
            Dataset summary dictionary
        """
        # Get sensor and target columns
        sensor_cols = [col for col in data.columns if col in self.config["sensor_descriptions"]]
        target_cols = [col for col in data.columns if col in self.config["target_mappings"]]
        
        # Create basic summary
        summary = {
            "dataset_name": self.dataset_name,
            "samples": len(data),
            "sensors": len(sensor_cols),
            "targets": len(target_cols),
            "sensor_descriptions": {k: v for k, v in self.config["sensor_descriptions"].items() if k in sensor_cols},
            "target_descriptions": {k: v for k, v in self.config["target_descriptions"].items() if k in target_cols}
        }
        
        # Add target distributions
        target_distributions = {}
        for target in target_cols:
            if target in data.columns:
                value_counts = data[target].value_counts().to_dict()
                
                # Convert keys to strings for JSON serialization
                value_counts = {str(k): int(v) for k, v in value_counts.items()}
                
                target_distributions[target] = value_counts
        
        summary["target_distributions"] = target_distributions
        
        # Add categorical target distributions
        category_cols = [col for col in data.columns if col.endswith("_category")]
        category_distributions = {}
        
        for col in category_cols:
            if col in data.columns:
                value_counts = data[col].value_counts().to_dict()
                category_distributions[col] = value_counts
        
        summary["category_distributions"] = category_distributions
        
        # Add critical condition counts
        critical_cols = [col for col in data.columns if col.endswith("_critical")]
        critical_counts = {}
        
        for col in critical_cols:
            if col in data.columns:
                critical_counts[col] = int(data[col].sum())
        
        summary["critical_conditions"] = critical_counts
        
        # Add sensor statistics
        sensor_stats = {}
        for sensor in sensor_cols:
            if sensor in data.columns:
                sensor_stats[sensor] = {
                    "mean": float(data[sensor].mean()),
                    "std": float(data[sensor].std()),
                    "min": float(data[sensor].min()),
                    "max": float(data[sensor].max())
                }
        
        summary["sensor_statistics"] = sensor_stats
        
        return summary
    
    def get_dataset_for_offer(self, offer_id: str) -> Dict[str, Any]:
        """
        Get dataset prepared for a specific offer.
        
        Args:
            offer_id: ID of the offer to prepare data for
            
        Returns:
            Dictionary with prepared dataset information
        """
        try:
            # Map offer IDs to specific data preparation methods
            offer_mappings = {
                "hydraulic_condition_monitoring": self._prepare_condition_monitoring,
                "predictive_maintenance": self._prepare_predictive_maintenance,
                "fault_detection": self._prepare_fault_detection,
                "system_health_monitoring": self._prepare_system_health_monitoring,
                "anomaly_detection": self._prepare_anomaly_detection
            }
            
            # Find the appropriate preparation method
            preparation_method = None
            for offer_prefix, method in offer_mappings.items():
                if offer_id.startswith(offer_prefix):
                    preparation_method = method
                    break
            
            # Use default method if no specific method found
            if preparation_method is None:
                preparation_method = self._prepare_condition_monitoring
            
            # Prepare the dataset
            result = preparation_method(offer_id)
            
            # Emit event
            self.emit_event(
                event_type="observe",
                payload={
                    "status": "dataset_prepared_for_offer",
                    "dataset": self.dataset_name,
                    "offer_id": offer_id,
                    "preparation_method": preparation_method.__name__
                }
            )
            
            return result
        except Exception as e:
            logger.error(f"Failed to prepare dataset for offer {offer_id}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_condition_monitoring(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for hydraulic condition monitoring offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.merged_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.merged_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Get sensor and target columns
        sensor_cols = [col for col in df.columns if col in self.config["sensor_descriptions"]]
        target_cols = [col for col in df.columns if col in self.config["target_mappings"]]
        category_cols = [col for col in df.columns if col.endswith("_category")]
        
        # Prepare the dataset
        prepared_df = df[["cycle_id"] + sensor_cols + target_cols + category_cols].copy()
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "condition_monitoring",
            "features": sensor_cols,
            "targets": target_cols,
            "categorical_targets": category_cols,
            "samples": len(prepared_df),
            "sensor_descriptions": {k: v for k, v in self.config["sensor_descriptions"].items() if k in sensor_cols},
            "target_descriptions": {k: v for k, v in self.config["target_descriptions"].items() if k in target_cols},
            "file_path": output_path
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_predictive_maintenance(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for hydraulic predictive maintenance offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.merged_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.merged_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Get sensor columns and critical condition columns
        sensor_cols = [col for col in df.columns if col in self.config["sensor_descriptions"]]
        critical_cols = [col for col in df.columns if col.endswith("_critical")]
        
        # Add rolling statistics columns
        rolling_cols = [col for col in df.columns if "_rolling_" in col]
        
        # Prepare the dataset
        selected_cols = ["cycle_id"] + sensor_cols + rolling_cols + critical_cols
        if "system_health" in df.columns:
            selected_cols.append("system_health")
        
        prepared_df = df[selected_cols].copy()
        
        # Create a maintenance window feature
        # 0: No maintenance needed
        # 1: Maintenance needed soon (next 5 cycles)
        # 2: Immediate maintenance needed
        prepared_df['maintenance_needed'] = (prepared_df[critical_cols].sum(axis=1) > 0).astype(int)
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "predictive_maintenance",
            "features": sensor_cols + rolling_cols,
            "targets": ["maintenance_needed"] + critical_cols,
            "samples": len(prepared_df),
            "maintenance_needed_count": int(prepared_df['maintenance_needed'].sum()),
            "critical_conditions": {col: int(prepared_df[col].sum()) for col in critical_cols},
            "sensor_descriptions": {k: v for k, v in self.config["sensor_descriptions"].items() if k in sensor_cols},
            "file_path": output_path
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_fault_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for hydraulic fault detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.merged_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.merged_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Get sensor columns
        sensor_cols = [col for col in df.columns if col in self.config["sensor_descriptions"]]
        
        # Prepare datasets for each component
        component_datasets = {}
        
        for component in ["cooler", "valve", "pump", "accumulator"]:
            if f"{component}_critical" in df.columns:
                # Create a dataset for this component
                component_df = df[["cycle_id"] + sensor_cols + [component, f"{component}_critical"]].copy()
                
                # Save component dataset
                output_dir = os.path.join(self.processed_dir, "offers")
                os.makedirs(output_dir, exist_ok=True)
                
                component_path = os.path.join(output_dir, f"{offer_id}_{component}_dataset.csv")
                component_df.to_csv(component_path, index=False)
                
                component_datasets[component] = {
                    "path": component_path,
                    "samples": len(component_df),
                    "critical_count": int(component_df[f"{component}_critical"].sum())
                }
        
        # Save prepared dataset (combined)
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        
        # Select columns for the combined dataset
        combined_cols = ["cycle_id"] + sensor_cols
        for component in ["cooler", "valve", "pump", "accumulator"]:
            if component in df.columns:
                combined_cols.append(component)
            if f"{component}_critical" in df.columns:
                combined_cols.append(f"{component}_critical")
        
        df[combined_cols].to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "fault_detection",
            "features": sensor_cols,
            "components": list(component_datasets.keys()),
            "samples": len(df),
            "component_datasets": component_datasets,
            "sensor_descriptions": {k: v for k, v in self.config["sensor_descriptions"].items() if k in sensor_cols},
            "file_paths": {
                "combined": output_path,
                **{component: info["path"] for component, info in component_datasets.items()}
            }
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "component_paths": {component: info["path"] for component, info in component_datasets.items()},
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_system_health_monitoring(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for hydraulic system health monitoring offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.merged_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.merged_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Get sensor columns and system health column
        sensor_cols = [col for col in df.columns if col in self.config["sensor_descriptions"]]
        
        # Ensure system_health column exists
        if "system_health" not in df.columns:
            # Create system health score based on component conditions
            component_cols = ["cooler", "valve", "pump", "accumulator"]
            component_cols = [col for col in component_cols if col in df.columns]
            
            if component_cols:
                # Normalize each component to 0-100 scale
                normalized_components = {}
                
                for component in component_cols:
                    if component == "cooler":
                        # 3: close to failure, 20: reduced, 100: full
                        normalized_components[component] = df[component].map({3: 0, 20: 50, 100: 100})
                    elif component == "valve":
                        # 100: optimal, 90: small lag, 80: severe lag, 73: close to failure
                        normalized_components[component] = df[component].map({73: 0, 80: 33, 90: 67, 100: 100})
                    elif component == "pump":
                        # 0: no leakage, 1: weak leakage, 2: severe leakage
                        normalized_components[component] = df[component].map({2: 0, 1: 50, 0: 100})
                    elif component == "accumulator":
                        # 130: optimal, 115: slightly reduced, 100: severely reduced, 90: close to failure
                        normalized_components[component] = df[component].map({90: 0, 100: 33, 115: 67, 130: 100})
                
                # Calculate system health as average of normalized components
                df["system_health"] = pd.DataFrame(normalized_components).mean(axis=1)
            else:
                # No component columns, use a default health score
                df["system_health"] = 100
        
        # Create health categories
        df["health_category"] = pd.cut(
            df["system_health"],
            bins=[0, 25, 50, 75, 100],
            labels=["critical", "poor", "fair", "good"]
        )
        
        # Prepare the dataset
        prepared_df = df[["cycle_id"] + sensor_cols + ["system_health", "health_category"]].copy()
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "system_health_monitoring",
            "features": sensor_cols,
            "targets": ["system_health", "health_category"],
            "samples": len(prepared_df),
            "health_distribution": prepared_df["health_category"].value_counts().to_dict(),
            "sensor_descriptions": {k: v for k, v in self.config["sensor_descriptions"].items() if k in sensor_cols},
            "file_path": output_path
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_anomaly_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for hydraulic anomaly detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.merged_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.merged_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Get sensor columns
        sensor_cols = [col for col in df.columns if col in self.config["sensor_descriptions"]]
        
        # Create anomaly indicator
        # An anomaly is defined as any critical condition
        critical_cols = [col for col in df.columns if col.endswith("_critical")]
        
        if critical_cols:
            df["anomaly"] = (df[critical_cols].sum(axis=1) > 0).astype(int)
        else:
            # If no critical columns, create anomaly based on system health
            if "system_health" in df.columns:
                df["anomaly"] = (df["system_health"] < 50).astype(int)
            else:
                # Create a dummy anomaly column (10% anomalies)
                np.random.seed(42)
                df["anomaly"] = (np.random.rand(len(df)) < 0.1).astype(int)
        
        # Prepare the dataset
        prepared_df = df[["cycle_id"] + sensor_cols + ["anomaly"]].copy()
        
        # Create a balanced dataset for anomaly detection
        normal_samples = prepared_df[prepared_df["anomaly"] == 0].sample(
            n=min(5000, (prepared_df["anomaly"] == 0).sum()),
            random_state=42
        )
        
        anomaly_samples = prepared_df[prepared_df["anomaly"] == 1]
        
        balanced_df = pd.concat([normal_samples, anomaly_samples])
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        balanced_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "anomaly_detection",
            "features": sensor_cols,
            "target": "anomaly",
            "samples": len(balanced_df),
            "normal_samples": int((balanced_df["anomaly"] == 0).sum()),
            "anomaly_samples": int(balanced_df["anomaly"].sum()),
            "sensor_descriptions": {k: v for k, v in self.config["sensor_descriptions"].items() if k in sensor_cols},
            "file_path": output_path
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create Hydraulic Systems dataset connector
    connector = HydraulicSystemsDatasetConnector()
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        data_dir="path/to/hydraulic_data"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("hydraulic_condition_monitoring_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
