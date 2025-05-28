"""
Turbofan Engine Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for the NASA Turbofan
Engine Degradation Simulation Dataset, supporting MCP/A2A integration.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union

from .dataset_connector_base import DatasetConnectorBase

logger = logging.getLogger(__name__)

class TurbofanDatasetConnector(DatasetConnectorBase):
    """
    Connector for NASA Turbofan Engine Degradation Simulation Dataset.
    
    This connector provides protocol-native ingestion, validation, and
    transformation for the NASA Turbofan Engine dataset, with support
    for predictive maintenance use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "turbofan-connector",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the Turbofan dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["aerospace", "manufacturing", "predictive_maintenance"],
            "column_mapping": {
                "unit_number": "unit",
                "time_cycles": "cycle",
                "operational_setting_1": "op_setting_1",
                "operational_setting_2": "op_setting_2",
                "operational_setting_3": "op_setting_3",
                "sensor_measurement_1": "s1",
                "sensor_measurement_2": "s2",
                "sensor_measurement_3": "s3",
                "sensor_measurement_4": "s4",
                "sensor_measurement_5": "s5",
                "sensor_measurement_6": "s6",
                "sensor_measurement_7": "s7",
                "sensor_measurement_8": "s8",
                "sensor_measurement_9": "s9",
                "sensor_measurement_10": "s10",
                "sensor_measurement_11": "s11",
                "sensor_measurement_12": "s12",
                "sensor_measurement_13": "s13",
                "sensor_measurement_14": "s14",
                "sensor_measurement_15": "s15",
                "sensor_measurement_16": "s16",
                "sensor_measurement_17": "s17",
                "sensor_measurement_18": "s18",
                "sensor_measurement_19": "s19",
                "sensor_measurement_20": "s20",
                "sensor_measurement_21": "s21"
            },
            "sensor_descriptions": {
                "s1": "Fan inlet temperature (°F)",
                "s2": "LPC outlet temperature (°F)",
                "s3": "HPC outlet temperature (°F)",
                "s4": "LPT outlet temperature (°F)",
                "s5": "Fan inlet pressure (psia)",
                "s6": "Bypass-duct pressure (psia)",
                "s7": "HPC outlet pressure (psia)",
                "s8": "Physical fan speed (rpm)",
                "s9": "Physical core speed (rpm)",
                "s10": "Engine pressure ratio (P50/P2)",
                "s11": "HPC outlet static pressure (psia)",
                "s12": "Ratio of fuel flow to Ps30 (pps/psia)",
                "s13": "Corrected fan speed (rpm)",
                "s14": "Corrected core speed (rpm)",
                "s15": "Bypass ratio",
                "s16": "Burner fuel-air ratio",
                "s17": "Bleed enthalpy",
                "s18": "Demanded fan speed (rpm)",
                "s19": "Demanded corrected fan speed (rpm)",
                "s20": "HPT coolant bleed (lbm/s)",
                "s21": "LPT coolant bleed (lbm/s)"
            },
            "important_sensors": ["s2", "s3", "s4", "s7", "s8", "s9", "s11", "s12", "s13", "s14", "s15", "s17", "s20", "s21"],
            "rul_threshold": 125  # Cycles before failure to mark as critical
        }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name="turbofan_engine",
            dataset_type="timeseries",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.train_dir = os.path.join(self.processed_dir, "train")
        self.test_dir = os.path.join(self.processed_dir, "test")
        self.rul_dir = os.path.join(self.processed_dir, "rul")
        
        os.makedirs(self.train_dir, exist_ok=True)
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.rul_dir, exist_ok=True)
        
        logger.info("Initialized Turbofan dataset connector")
    
    def ingest_dataset(
        self,
        train_file: str,
        test_file: str,
        rul_file: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the complete Turbofan dataset.
        
        Args:
            train_file: Path to the training data file
            test_file: Path to the test data file
            rul_file: Path to the RUL (remaining useful life) data file
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
                        "files": {
                            "train": train_file,
                            "test": test_file,
                            "rul": rul_file
                        }
                    }
                )
            
            # Ingest training data
            train_result = self.ingest_data(
                source_path=train_file,
                validate=validate,
                transform=transform,
                emit_events=False
            )
            
            # Ingest test data
            test_result = self.ingest_data(
                source_path=test_file,
                validate=validate,
                transform=transform,
                emit_events=False
            )
            
            # Ingest RUL data
            rul_result = self.ingest_data(
                source_path=rul_file,
                validate=validate,
                transform=transform,
                emit_events=False
            )
            
            # Process the complete dataset
            if transform and train_result["success"] and test_result["success"] and rul_result["success"]:
                self._process_complete_dataset(
                    train_path=train_result["processed_path"],
                    test_path=test_result["processed_path"],
                    rul_path=rul_result["processed_path"]
                )
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "success": train_result["success"] and test_result["success"] and rul_result["success"],
                "status": "dataset_ingestion_completed",
                "components": {
                    "train": train_result,
                    "test": test_result,
                    "rul": rul_result
                },
                "statistics": self.metadata["statistics"],
                "duration": duration
            }
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_ingestion_completed",
                        "dataset": self.dataset_name,
                        "statistics": self.metadata["statistics"],
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
    
    def _load_data(self, source_path: str) -> pd.DataFrame:
        """
        Load data from source path.
        
        Args:
            source_path: Path to the source data
            
        Returns:
            Loaded data as DataFrame
        """
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Determine file type and load accordingly
        if source_path.endswith('.txt'):
            # NASA Turbofan dataset uses space-delimited text files
            if "RUL" in source_path:
                # RUL file has a single column with no header
                df = pd.read_csv(source_path, header=None, delim_whitespace=True)
                df.columns = ["RUL"]
            else:
                # Training and test files have the same format
                column_names = [
                    "unit", "cycle", 
                    "op_setting_1", "op_setting_2", "op_setting_3",
                    "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", 
                    "s11", "s12", "s13", "s14", "s15", "s16", "s17", "s18", "s19", "s20", "s21"
                ]
                df = pd.read_csv(source_path, header=None, delim_whitespace=True)
                
                # Ensure the correct number of columns
                if len(df.columns) == len(column_names):
                    df.columns = column_names
                else:
                    logger.warning(f"Column count mismatch: expected {len(column_names)}, got {len(df.columns)}")
                    # Use available columns
                    df.columns = column_names[:len(df.columns)]
        elif source_path.endswith('.csv'):
            df = pd.read_csv(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        return df
    
    def _validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the Turbofan dataset.
        
        Args:
            data: Data to validate
            
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
        
        # Check for expected columns in training/test data
        if "unit" in data.columns and "cycle" in data.columns:
            # This is training or test data
            expected_columns = ["unit", "cycle", "op_setting_1", "op_setting_2", "op_setting_3"]
            expected_columns.extend([f"s{i}" for i in range(1, 22)])
            
            missing_columns = [col for col in expected_columns if col not in data.columns]
            if missing_columns:
                warnings.append(f"Missing expected columns: {missing_columns}")
            
            # Check data types
            if not pd.api.types.is_numeric_dtype(data["unit"]):
                errors.append("Column 'unit' is not numeric")
            
            if not pd.api.types.is_numeric_dtype(data["cycle"]):
                errors.append("Column 'cycle' is not numeric")
            
            # Check for negative cycles
            if (data["cycle"] < 0).any():
                errors.append("Negative cycle values found")
            
            # Check for duplicate (unit, cycle) combinations
            duplicates = data.duplicated(subset=["unit", "cycle"]).sum()
            if duplicates > 0:
                errors.append(f"Found {duplicates} duplicate (unit, cycle) combinations")
        
        # Check for expected columns in RUL data
        elif "RUL" in data.columns:
            # This is RUL data
            if not pd.api.types.is_numeric_dtype(data["RUL"]):
                errors.append("Column 'RUL' is not numeric")
            
            # Check for negative RUL values
            if (data["RUL"] < 0).any():
                errors.append("Negative RUL values found")
        
        # Check for missing values
        missing_count = data.isna().sum().sum()
        if missing_count > 0:
            warnings.append(f"Data contains {missing_count} missing values")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the Turbofan dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Handle different data types
        if "unit" in df.columns and "cycle" in df.columns:
            # This is training or test data
            
            # Fill missing values
            df = df.fillna(method='ffill')
            
            # Add normalized cycle column
            df_with_max_cycle = df.groupby('unit')['cycle'].transform('max')
            df['normalized_cycle'] = df['cycle'] / df_with_max_cycle
            
            # Calculate remaining useful life for training data
            # RUL = max cycle - current cycle
            df['RUL'] = df.groupby('unit')['cycle'].transform('max') - df['cycle']
            
            # Add RUL category
            rul_threshold = self.config.get("rul_threshold", 125)
            df['RUL_category'] = pd.cut(
                df['RUL'],
                bins=[-1, 20, rul_threshold, float('inf')],
                labels=['critical', 'warning', 'normal']
            )
            
            # Calculate sensor moving averages
            important_sensors = self.config.get("important_sensors", [])
            for sensor in important_sensors:
                if sensor in df.columns:
                    df[f"{sensor}_ma5"] = df.groupby('unit')[sensor].transform(
                        lambda x: x.rolling(window=5, min_periods=1).mean()
                    )
            
            # Calculate sensor trends (slope over last 5 cycles)
            for sensor in important_sensors:
                if sensor in df.columns:
                    df[f"{sensor}_trend"] = df.groupby('unit')[sensor].transform(
                        lambda x: x.rolling(window=5, min_periods=3).apply(
                            lambda y: np.polyfit(range(len(y)), y, 1)[0] if len(y) >= 3 else np.nan
                        )
                    )
            
            # Fill NaN values in trend columns
            trend_columns = [col for col in df.columns if col.endswith('_trend')]
            df[trend_columns] = df[trend_columns].fillna(0)
        
        elif "RUL" in df.columns:
            # This is RUL data
            # Add unit number as index
            df['unit'] = df.index + 1
            
            # Add RUL category
            rul_threshold = self.config.get("rul_threshold", 125)
            df['RUL_category'] = pd.cut(
                df['RUL'],
                bins=[-1, 20, rul_threshold, float('inf')],
                labels=['critical', 'warning', 'normal']
            )
        
        return df
    
    def _process_complete_dataset(
        self,
        train_path: str,
        test_path: str,
        rul_path: str
    ) -> Dict[str, str]:
        """
        Process the complete dataset after individual files are ingested.
        
        Args:
            train_path: Path to the processed training data
            test_path: Path to the processed test data
            rul_path: Path to the processed RUL data
            
        Returns:
            Dictionary of output file paths
        """
        try:
            # Load processed data
            train_df = pd.read_csv(train_path)
            test_df = pd.read_csv(test_path)
            rul_df = pd.read_csv(rul_path)
            
            # Merge test data with RUL data
            test_units = test_df['unit'].unique()
            
            # Create a mapping of unit to true RUL
            rul_mapping = {}
            for i, unit in enumerate(test_units):
                if i < len(rul_df):
                    rul_mapping[unit] = rul_df.iloc[i]['RUL']
            
            # Apply true RUL to test data
            test_with_rul = test_df.copy()
            test_with_rul['true_RUL'] = test_with_rul['unit'].map(rul_mapping)
            
            # Calculate error between predicted and true RUL
            test_with_rul['RUL_error'] = test_with_rul['RUL'] - test_with_rul['true_RUL']
            
            # Save merged test data
            merged_test_path = os.path.join(self.test_dir, "test_with_true_rul.csv")
            test_with_rul.to_csv(merged_test_path, index=False)
            
            # Create a dataset summary
            summary = {
                "dataset_name": self.dataset_name,
                "train_units": len(train_df['unit'].unique()),
                "test_units": len(test_df['unit'].unique()),
                "total_train_samples": len(train_df),
                "total_test_samples": len(test_df),
                "features": {
                    "operational_settings": ["op_setting_1", "op_setting_2", "op_setting_3"],
                    "sensors": [f"s{i}" for i in range(1, 22)],
                    "important_sensors": self.config.get("important_sensors", [])
                },
                "sensor_descriptions": self.config.get("sensor_descriptions", {}),
                "rul_statistics": {
                    "min_rul": float(train_df['RUL'].min()),
                    "max_rul": float(train_df['RUL'].max()),
                    "mean_rul": float(train_df['RUL'].mean()),
                    "critical_samples": int(train_df[train_df['RUL_category'] == 'critical'].shape[0]),
                    "warning_samples": int(train_df[train_df['RUL_category'] == 'warning'].shape[0]),
                    "normal_samples": int(train_df[train_df['RUL_category'] == 'normal'].shape[0])
                }
            }
            
            # Save summary
            summary_path = os.path.join(self.metadata_dir, "dataset_summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Update metadata with summary
            self.metadata["dataset_summary"] = summary
            self._save_metadata()
            
            logger.info(f"Processed complete dataset and saved summary to {summary_path}")
            
            return {
                "merged_test": merged_test_path,
                "summary": summary_path
            }
        except Exception as e:
            logger.error(f"Failed to process complete dataset: {str(e)}")
            return {}
    
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
                "predictive_maintenance_basic": self._prepare_basic_predictive_maintenance,
                "predictive_maintenance_advanced": self._prepare_advanced_predictive_maintenance,
                "anomaly_detection": self._prepare_anomaly_detection,
                "remaining_useful_life": self._prepare_remaining_useful_life,
                "condition_monitoring": self._prepare_condition_monitoring
            }
            
            # Find the appropriate preparation method
            preparation_method = None
            for offer_prefix, method in offer_mappings.items():
                if offer_id.startswith(offer_prefix):
                    preparation_method = method
                    break
            
            # Use default method if no specific method found
            if preparation_method is None:
                preparation_method = self._prepare_basic_predictive_maintenance
            
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
    
    def _prepare_basic_predictive_maintenance(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for basic predictive maintenance offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed training data
        train_files = [f for f in os.listdir(self.train_dir) if f.endswith('.csv')]
        if not train_files:
            return {"success": False, "error": "No processed training data found"}
        
        latest_train = sorted(train_files)[-1]
        train_path = os.path.join(self.train_dir, latest_train)
        
        # Load the data
        df = pd.read_csv(train_path)
        
        # Select only important features
        important_sensors = self.config.get("important_sensors", [])
        selected_columns = ["unit", "cycle", "RUL", "RUL_category"] + important_sensors
        
        # Filter to columns that exist in the dataframe
        selected_columns = [col for col in selected_columns if col in df.columns]
        
        # Prepare the dataset
        prepared_df = df[selected_columns].copy()
        
        # Add binary classification target (1 if RUL <= 30, 0 otherwise)
        prepared_df['failure_imminent'] = (prepared_df['RUL'] <= 30).astype(int)
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "basic_predictive_maintenance",
            "features": selected_columns,
            "target": "failure_imminent",
            "samples": len(prepared_df),
            "positive_samples": int(prepared_df['failure_imminent'].sum()),
            "negative_samples": int((prepared_df['failure_imminent'] == 0).sum()),
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
    
    def _prepare_advanced_predictive_maintenance(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for advanced predictive maintenance offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed training data
        train_files = [f for f in os.listdir(self.train_dir) if f.endswith('.csv')]
        if not train_files:
            return {"success": False, "error": "No processed training data found"}
        
        latest_train = sorted(train_files)[-1]
        train_path = os.path.join(self.train_dir, latest_train)
        
        # Load the data
        df = pd.read_csv(train_path)
        
        # Select features including derived features
        important_sensors = self.config.get("important_sensors", [])
        trend_features = [f"{sensor}_trend" for sensor in important_sensors if f"{sensor}_trend" in df.columns]
        ma_features = [f"{sensor}_ma5" for sensor in important_sensors if f"{sensor}_ma5" in df.columns]
        
        selected_columns = ["unit", "cycle", "normalized_cycle", "RUL", "RUL_category"] + important_sensors + trend_features + ma_features
        
        # Filter to columns that exist in the dataframe
        selected_columns = [col for col in selected_columns if col in df.columns]
        
        # Prepare the dataset
        prepared_df = df[selected_columns].copy()
        
        # Add multi-class classification target
        prepared_df['maintenance_window'] = pd.cut(
            prepared_df['RUL'],
            bins=[-1, 20, 50, 125, float('inf')],
            labels=['immediate', 'short_term', 'medium_term', 'long_term']
        )
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "advanced_predictive_maintenance",
            "features": selected_columns,
            "derived_features": trend_features + ma_features,
            "target": "maintenance_window",
            "target_classes": ['immediate', 'short_term', 'medium_term', 'long_term'],
            "samples": len(prepared_df),
            "class_distribution": prepared_df['maintenance_window'].value_counts().to_dict(),
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
        Prepare dataset for anomaly detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed training data
        train_files = [f for f in os.listdir(self.train_dir) if f.endswith('.csv')]
        if not train_files:
            return {"success": False, "error": "No processed training data found"}
        
        latest_train = sorted(train_files)[-1]
        train_path = os.path.join(self.train_dir, latest_train)
        
        # Load the data
        df = pd.read_csv(train_path)
        
        # Select sensor features
        sensor_columns = [f"s{i}" for i in range(1, 22) if f"s{i}" in df.columns]
        selected_columns = ["unit", "cycle", "RUL"] + sensor_columns
        
        # Prepare the dataset
        prepared_df = df[selected_columns].copy()
        
        # Add anomaly label (1 if RUL <= 30, 0 otherwise)
        prepared_df['anomaly'] = (prepared_df['RUL'] <= 30).astype(int)
        
        # Create a balanced dataset for anomaly detection
        normal_samples = prepared_df[prepared_df['anomaly'] == 0].sample(
            n=min(5000, (prepared_df['anomaly'] == 0).sum()),
            random_state=42
        )
        
        anomaly_samples = prepared_df[prepared_df['anomaly'] == 1]
        
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
            "features": sensor_columns,
            "target": "anomaly",
            "samples": len(balanced_df),
            "normal_samples": int((balanced_df['anomaly'] == 0).sum()),
            "anomaly_samples": int(balanced_df['anomaly'].sum()),
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
    
    def _prepare_remaining_useful_life(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for remaining useful life prediction offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed training and test data
        train_files = [f for f in os.listdir(self.train_dir) if f.endswith('.csv')]
        test_files = [f for f in os.listdir(self.test_dir) if f.endswith('.csv') and "true_rul" in f]
        
        if not train_files or not test_files:
            return {"success": False, "error": "No processed training or test data found"}
        
        latest_train = sorted(train_files)[-1]
        latest_test = sorted(test_files)[-1]
        
        train_path = os.path.join(self.train_dir, latest_train)
        test_path = os.path.join(self.test_dir, latest_test)
        
        # Load the data
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)
        
        # Select features
        important_sensors = self.config.get("important_sensors", [])
        selected_columns = ["unit", "cycle", "RUL"] + important_sensors
        
        # Filter to columns that exist in both dataframes
        selected_columns = [col for col in selected_columns if col in train_df.columns and col in test_df.columns]
        
        # Prepare the datasets
        train_prepared = train_df[selected_columns].copy()
        
        test_selected_columns = [col for col in selected_columns if col in test_df.columns]
        test_prepared = test_df[test_selected_columns].copy()
        
        if "true_RUL" in test_df.columns:
            test_prepared["true_RUL"] = test_df["true_RUL"]
        
        # Save prepared datasets
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        train_output_path = os.path.join(output_dir, f"{offer_id}_train.csv")
        test_output_path = os.path.join(output_dir, f"{offer_id}_test.csv")
        
        train_prepared.to_csv(train_output_path, index=False)
        test_prepared.to_csv(test_output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "remaining_useful_life",
            "features": important_sensors,
            "target": "RUL",
            "train_samples": len(train_prepared),
            "test_samples": len(test_prepared),
            "rul_statistics": {
                "min_rul": float(train_prepared['RUL'].min()),
                "max_rul": float(train_prepared['RUL'].max()),
                "mean_rul": float(train_prepared['RUL'].mean()),
                "std_rul": float(train_prepared['RUL'].std())
            },
            "train_file_path": train_output_path,
            "test_file_path": test_output_path
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "train_dataset_path": train_output_path,
            "test_dataset_path": test_output_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_condition_monitoring(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for condition monitoring offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed training data
        train_files = [f for f in os.listdir(self.train_dir) if f.endswith('.csv')]
        if not train_files:
            return {"success": False, "error": "No processed training data found"}
        
        latest_train = sorted(train_files)[-1]
        train_path = os.path.join(self.train_dir, latest_train)
        
        # Load the data
        df = pd.read_csv(train_path)
        
        # Select features for condition monitoring
        sensor_columns = [f"s{i}" for i in range(1, 22) if f"s{i}" in df.columns]
        op_setting_columns = [f"op_setting_{i}" for i in range(1, 4) if f"op_setting_{i}" in df.columns]
        
        selected_columns = ["unit", "cycle"] + op_setting_columns + sensor_columns
        
        # Filter to columns that exist in the dataframe
        selected_columns = [col for col in selected_columns if col in df.columns]
        
        # Prepare the dataset - sample data points for visualization
        # Take data from multiple units with different health states
        units = df['unit'].unique()
        
        # Select a few units for demonstration
        if len(units) >= 3:
            selected_units = [units[0], units[len(units)//2], units[-1]]
        else:
            selected_units = units
        
        prepared_df = df[df['unit'].isin(selected_units)][selected_columns].copy()
        
        # Add health state based on RUL
        if 'RUL' in df.columns:
            prepared_df['RUL'] = df.loc[prepared_df.index, 'RUL']
            prepared_df['health_state'] = pd.cut(
                prepared_df['RUL'],
                bins=[-1, 20, 50, 125, float('inf')],
                labels=['critical', 'warning', 'moderate', 'healthy']
            )
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create sensor description mapping for visualization
        sensor_descriptions = self.config.get("sensor_descriptions", {})
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "condition_monitoring",
            "features": selected_columns,
            "sensor_descriptions": {k: v for k, v in sensor_descriptions.items() if k in sensor_columns},
            "operational_settings": op_setting_columns,
            "units": selected_units.tolist(),
            "samples": len(prepared_df),
            "samples_per_unit": prepared_df.groupby('unit').size().to_dict(),
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
    
    # Create Turbofan dataset connector
    connector = TurbofanDatasetConnector()
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        train_file="path/to/train_FD001.txt",
        test_file="path/to/test_FD001.txt",
        rul_file="path/to/RUL_FD001.txt"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("predictive_maintenance_basic_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
