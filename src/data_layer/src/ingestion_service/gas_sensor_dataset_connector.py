"""
Gas Sensor Array Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for the Gas Sensor Array Drift
dataset, supporting MCP/A2A integration for industrial monitoring applications.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from sklearn.preprocessing import StandardScaler, LabelEncoder

from .dataset_connector_base import DatasetConnectorBase

logger = logging.getLogger(__name__)

class GasSensorDatasetConnector(DatasetConnectorBase):
    """
    Connector for Gas Sensor Array Drift Dataset.
    
    This connector provides protocol-native ingestion, validation, and
    transformation for the Gas Sensor Array Drift dataset, with support
    for gas detection and concentration monitoring use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "gas-sensor-connector",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the Gas Sensor Array dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "chemical", "gas_detection"],
            "intelligence_type": "sensor_fusion",
            "batch_files": {
                "batch1": "batch1.dat",
                "batch2": "batch2.dat",
                "batch3": "batch3.dat",
                "batch4": "batch4.dat",
                "batch5": "batch5.dat",
                "batch6": "batch6.dat",
                "batch7": "batch7.dat",
                "batch8": "batch8.dat",
                "batch9": "batch9.dat",
                "batch10": "batch10.dat"
            },
            "gas_types": {
                1: "Ethanol",
                2: "Ethylene",
                3: "Ammonia",
                4: "Acetaldehyde",
                5: "Acetone",
                6: "Toluene"
            },
            "concentration_levels": {
                1: "50 ppm",
                2: "100 ppm",
                3: "500 ppm",
                4: "1000 ppm"
            },
            "sensor_names": [
                "S1_DR", "S2_DR", "S3_DR", "S4_DR", "S5_DR", "S6_DR", 
                "S7_DR", "S8_DR", "S9_DR", "S10_DR", "S11_DR", "S12_DR", 
                "S13_DR", "S14_DR", "S15_DR", "S16_DR"
            ],
            "feature_columns": list(range(1, 129)),  # 128 features (16 sensors × 8 features per sensor)
            "target_columns": {
                "gas_type": 0,
                "concentration": 129
            },
            "metadata_columns": {
                "batch_id": 130,
                "time_stamp": 131
            }
        }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name="gas_sensor_array",
            dataset_type="timeseries",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.batches_dir = os.path.join(self.processed_dir, "batches")
        self.merged_dir = os.path.join(self.processed_dir, "merged")
        self.models_dir = os.path.join(self.processed_dir, "models")
        
        os.makedirs(self.batches_dir, exist_ok=True)
        os.makedirs(self.merged_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("Initialized Gas Sensor Array dataset connector")
    
    def ingest_dataset(
        self,
        data_dir: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the complete Gas Sensor Array dataset.
        
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
            
            # Ingest batch files
            batch_results = {}
            for batch_name, batch_file in self.config["batch_files"].items():
                file_path = os.path.join(data_dir, batch_file)
                if os.path.exists(file_path):
                    batch_results[batch_name] = self.ingest_data(
                        source_path=file_path,
                        validate=validate,
                        transform=False,  # We'll transform after merging
                        emit_events=False,
                        metadata={"batch_name": batch_name}
                    )
                else:
                    logger.warning(f"Batch file not found: {file_path}")
            
            # Process the complete dataset
            if batch_results:
                merged_result = self._process_complete_dataset(
                    batch_results=batch_results,
                    transform=transform
                )
            else:
                merged_result = {
                    "success": False,
                    "error": "Failed to ingest any batch data"
                }
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "success": merged_result["success"],
                "status": "dataset_ingestion_completed" if merged_result["success"] else "dataset_ingestion_failed",
                "components": {
                    "batches": batch_results,
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
        if source_path.endswith('.dat'):
            # The dataset uses space-delimited data files
            df = pd.read_csv(source_path, header=None, delimiter=' ')
            
            # Add batch information if available
            if metadata and "batch_name" in metadata:
                batch_name = metadata["batch_name"]
                batch_id = int(batch_name.replace("batch", ""))
                
                # Add batch_id column if not present
                if len(df.columns) <= self.config["metadata_columns"]["batch_id"]:
                    df[self.config["metadata_columns"]["batch_id"]] = batch_id
        elif source_path.endswith('.csv'):
            df = pd.read_csv(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        return df
    
    def _validate_data(self, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate the Gas Sensor Array dataset.
        
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
        
        # Check for expected columns
        expected_columns = max(self.config["feature_columns"]) + 1  # Features are 1-indexed
        if len(data.columns) < expected_columns:
            errors.append(f"Expected at least {expected_columns} columns, found {len(data.columns)}")
        
        # Check for gas type and concentration columns
        gas_type_col = self.config["target_columns"]["gas_type"]
        concentration_col = self.config["target_columns"]["concentration"]
        
        if gas_type_col >= len(data.columns):
            errors.append(f"Gas type column {gas_type_col} not found")
        else:
            # Check gas type values
            gas_types = data[gas_type_col].unique()
            valid_gas_types = list(self.config["gas_types"].keys())
            invalid_gas_types = [gt for gt in gas_types if gt not in valid_gas_types]
            
            if invalid_gas_types:
                warnings.append(f"Invalid gas types found: {invalid_gas_types}")
        
        if concentration_col >= len(data.columns):
            errors.append(f"Concentration column {concentration_col} not found")
        else:
            # Check concentration values
            concentrations = data[concentration_col].unique()
            valid_concentrations = list(self.config["concentration_levels"].keys())
            invalid_concentrations = [c for c in concentrations if c not in valid_concentrations]
            
            if invalid_concentrations:
                warnings.append(f"Invalid concentration levels found: {invalid_concentrations}")
        
        # Check for numeric data types in feature columns
        non_numeric_cols = []
        for col in self.config["feature_columns"]:
            if col < len(data.columns) and not pd.api.types.is_numeric_dtype(data[col]):
                non_numeric_cols.append(col)
        
        if non_numeric_cols:
            errors.append(f"Non-numeric feature columns found: {non_numeric_cols}")
        
        # Check for missing values in feature columns
        missing_counts = {}
        for col in self.config["feature_columns"]:
            if col < len(data.columns):
                missing_count = data[col].isna().sum()
                if missing_count > 0:
                    missing_counts[col] = missing_count
        
        if missing_counts:
            warnings.append(f"Missing values found in {len(missing_counts)} columns: {missing_counts}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _process_complete_dataset(
        self,
        batch_results: Dict[str, Dict[str, Any]],
        transform: bool = True
    ) -> Dict[str, Any]:
        """
        Process the complete dataset after individual batch files are ingested.
        
        Args:
            batch_results: Results from batch data ingestion
            transform: Whether to transform the data
            
        Returns:
            Processing result information
        """
        try:
            # Load raw batch data
            batch_dfs = {}
            for batch_name, result in batch_results.items():
                if result["success"] and "raw_path" in result:
                    batch_dfs[batch_name] = pd.read_csv(result["raw_path"])
            
            if not batch_dfs:
                return {
                    "success": False,
                    "error": "No batch data to process"
                }
            
            # Merge all batch data
            merged_df = pd.concat(batch_dfs.values(), ignore_index=True)
            
            # Save merged raw data
            merged_raw_path = os.path.join(self.merged_dir, "gas_sensor_array_raw.csv")
            merged_df.to_csv(merged_raw_path, index=False)
            
            # Transform data if requested
            if transform:
                transformed_df = self._transform_data(merged_df)
                
                # Save transformed data
                transformed_path = os.path.join(self.merged_dir, "gas_sensor_array_transformed.csv")
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
        Transform the Gas Sensor Array dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Rename columns for better readability
        column_mapping = {}
        
        # Feature columns (sensor readings)
        for i, col in enumerate(self.config["feature_columns"]):
            # Calculate sensor index (1-16) and feature index (1-8)
            sensor_idx = (i // 8) + 1
            feature_idx = (i % 8) + 1
            
            # Create readable column name
            column_mapping[col] = f"S{sensor_idx}_F{feature_idx}"
        
        # Target columns
        gas_type_col = self.config["target_columns"]["gas_type"]
        concentration_col = self.config["target_columns"]["concentration"]
        
        column_mapping[gas_type_col] = "gas_type"
        column_mapping[concentration_col] = "concentration"
        
        # Metadata columns
        for meta_name, meta_col in self.config["metadata_columns"].items():
            column_mapping[meta_col] = meta_name
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Add readable gas type and concentration labels
        df["gas_name"] = df["gas_type"].map(self.config["gas_types"])
        df["concentration_level"] = df["concentration"].map(self.config["concentration_levels"])
        
        # Handle missing values in sensor readings
        sensor_cols = [col for col in df.columns if col.startswith("S") and "_F" in col]
        
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
        
        # Encode categorical variables
        label_encoders = {}
        
        for cat_col in ["gas_type", "concentration"]:
            if cat_col in df.columns:
                le = LabelEncoder()
                df[f"{cat_col}_encoded"] = le.fit_transform(df[cat_col])
                
                # Save the encoder
                encoder_path = os.path.join(self.models_dir, f"{cat_col}_encoder.pkl")
                with open(encoder_path, 'wb') as f:
                    pickle.dump(le, f)
                
                label_encoders[cat_col] = le
        
        # Create a combined target for multi-class classification
        if "gas_type" in df.columns and "concentration" in df.columns:
            df["combined_target"] = df["gas_type"].astype(str) + "_" + df["concentration"].astype(str)
            
            # Encode the combined target
            le = LabelEncoder()
            df["combined_target_encoded"] = le.fit_transform(df["combined_target"])
            
            # Save the encoder
            encoder_path = os.path.join(self.models_dir, "combined_target_encoder.pkl")
            with open(encoder_path, 'wb') as f:
                pickle.dump(le, f)
        
        # Add batch information if not present
        if "batch_id" not in df.columns:
            df["batch_id"] = 0
        
        # Add drift indicator (time-based)
        if "time_stamp" in df.columns:
            # Normalize time to 0-1 range
            min_time = df["time_stamp"].min()
            max_time = df["time_stamp"].max()
            
            if max_time > min_time:
                df["normalized_time"] = (df["time_stamp"] - min_time) / (max_time - min_time)
            else:
                df["normalized_time"] = 0
            
            # Create drift indicator (early vs late measurements)
            df["drift_indicator"] = (df["normalized_time"] > 0.5).astype(int)
        
        # Calculate sensor correlations
        sensor_corr = df[sensor_cols].corr()
        
        # Save correlation matrix
        corr_path = os.path.join(self.metadata_dir, "sensor_correlations.csv")
        sensor_corr.to_csv(corr_path)
        
        # Create sensor groups based on correlation
        # Group sensors that are highly correlated (> 0.8)
        sensor_groups = {}
        processed_sensors = set()
        
        for i, sensor1 in enumerate(sensor_cols):
            if sensor1 in processed_sensors:
                continue
                
            group = [sensor1]
            processed_sensors.add(sensor1)
            
            for sensor2 in sensor_cols[i+1:]:
                if sensor2 in processed_sensors:
                    continue
                    
                if abs(sensor_corr.loc[sensor1, sensor2]) > 0.8:
                    group.append(sensor2)
                    processed_sensors.add(sensor2)
            
            if len(group) > 1:
                group_name = f"sensor_group_{len(sensor_groups) + 1}"
                sensor_groups[group_name] = group
                
                # Add group average
                df[group_name + "_avg"] = df[group].mean(axis=1)
        
        # Save sensor groups
        groups_path = os.path.join(self.metadata_dir, "sensor_groups.json")
        with open(groups_path, 'w') as f:
            json.dump(sensor_groups, f, indent=2)
        
        return df
    
    def _create_dataset_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create a summary of the dataset.
        
        Args:
            data: Processed dataset
            
        Returns:
            Dataset summary dictionary
        """
        # Get sensor columns
        sensor_cols = [col for col in data.columns if col.startswith("S") and "_F" in col]
        
        # Create basic summary
        summary = {
            "dataset_name": self.dataset_name,
            "samples": len(data),
            "sensors": len(set([col.split("_")[0] for col in sensor_cols])),
            "features_per_sensor": len(set([col.split("_")[1] for col in sensor_cols])),
            "total_features": len(sensor_cols)
        }
        
        # Add gas type distribution
        if "gas_type" in data.columns and "gas_name" in data.columns:
            gas_counts = data.groupby(["gas_type", "gas_name"]).size().reset_index()
            gas_counts.columns = ["gas_type", "gas_name", "count"]
            
            gas_distribution = {}
            for _, row in gas_counts.iterrows():
                gas_distribution[row["gas_name"]] = int(row["count"])
            
            summary["gas_distribution"] = gas_distribution
        
        # Add concentration distribution
        if "concentration" in data.columns and "concentration_level" in data.columns:
            conc_counts = data.groupby(["concentration", "concentration_level"]).size().reset_index()
            conc_counts.columns = ["concentration", "concentration_level", "count"]
            
            conc_distribution = {}
            for _, row in conc_counts.iterrows():
                conc_distribution[row["concentration_level"]] = int(row["count"])
            
            summary["concentration_distribution"] = conc_distribution
        
        # Add batch distribution
        if "batch_id" in data.columns:
            batch_counts = data["batch_id"].value_counts().to_dict()
            batch_distribution = {f"batch{k}": int(v) for k, v in batch_counts.items()}
            
            summary["batch_distribution"] = batch_distribution
        
        # Add drift information
        if "drift_indicator" in data.columns:
            drift_counts = data["drift_indicator"].value_counts().to_dict()
            
            summary["drift_distribution"] = {
                "early_measurements": int(drift_counts.get(0, 0)),
                "late_measurements": int(drift_counts.get(1, 0))
            }
        
        # Add sensor statistics
        sensor_stats = {}
        for sensor in set([col.split("_")[0] for col in sensor_cols]):
            sensor_features = [col for col in sensor_cols if col.startswith(sensor)]
            
            sensor_stats[sensor] = {
                "features": len(sensor_features),
                "mean": float(data[sensor_features].values.mean()),
                "std": float(data[sensor_features].values.std()),
                "min": float(data[sensor_features].values.min()),
                "max": float(data[sensor_features].values.max())
            }
        
        summary["sensor_statistics"] = sensor_stats
        
        # Add sensor group information
        groups_path = os.path.join(self.metadata_dir, "sensor_groups.json")
        if os.path.exists(groups_path):
            with open(groups_path, 'r') as f:
                sensor_groups = json.load(f)
            
            summary["sensor_groups"] = {
                "count": len(sensor_groups),
                "groups": sensor_groups
            }
        
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
                "gas_detection": self._prepare_gas_detection,
                "gas_concentration": self._prepare_gas_concentration,
                "drift_detection": self._prepare_drift_detection,
                "sensor_fusion": self._prepare_sensor_fusion,
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
                preparation_method = self._prepare_gas_detection
            
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
    
    def _prepare_gas_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for gas detection offer.
        
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
        sensor_cols = [col for col in df.columns if col.startswith("S") and "_F" in col]
        
        # Prepare the dataset for gas detection (classification)
        if "gas_type" in df.columns and "gas_name" in df.columns:
            # Create a dataset for gas type classification
            prepared_df = df[sensor_cols + ["gas_type", "gas_name", "gas_type_encoded"]].copy()
            
            # Save prepared dataset
            output_dir = os.path.join(self.processed_dir, "offers")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
            prepared_df.to_csv(output_path, index=False)
            
            # Create metadata
            metadata = {
                "offer_id": offer_id,
                "dataset_name": self.dataset_name,
                "preparation_method": "gas_detection",
                "features": sensor_cols,
                "target": "gas_type",
                "target_readable": "gas_name",
                "target_encoded": "gas_type_encoded",
                "samples": len(prepared_df),
                "classes": len(prepared_df["gas_type"].unique()),
                "class_distribution": prepared_df["gas_name"].value_counts().to_dict(),
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
        else:
            return {
                "success": False,
                "error": "Gas type information not found in dataset"
            }
    
    def _prepare_gas_concentration(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for gas concentration prediction offer.
        
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
        sensor_cols = [col for col in df.columns if col.startswith("S") and "_F" in col]
        
        # Prepare datasets for each gas type
        gas_datasets = {}
        
        if "gas_type" in df.columns and "concentration" in df.columns:
            for gas_type, gas_name in self.config["gas_types"].items():
                # Filter data for this gas type
                gas_df = df[df["gas_type"] == gas_type].copy()
                
                if len(gas_df) > 0:
                    # Create a dataset for concentration prediction
                    gas_prepared_df = gas_df[sensor_cols + ["concentration", "concentration_level", "concentration_encoded"]].copy()
                    
                    # Save gas-specific dataset
                    output_dir = os.path.join(self.processed_dir, "offers")
                    os.makedirs(output_dir, exist_ok=True)
                    
                    gas_path = os.path.join(output_dir, f"{offer_id}_{gas_name.lower()}_dataset.csv")
                    gas_prepared_df.to_csv(gas_path, index=False)
                    
                    gas_datasets[gas_name] = {
                        "path": gas_path,
                        "samples": len(gas_prepared_df),
                        "concentration_distribution": gas_prepared_df["concentration_level"].value_counts().to_dict()
                    }
            
            # Create a combined dataset for all gases
            combined_df = df[["gas_type", "gas_name"] + sensor_cols + ["concentration", "concentration_level", "concentration_encoded"]].copy()
            
            # Save combined dataset
            output_dir = os.path.join(self.processed_dir, "offers")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
            combined_df.to_csv(output_path, index=False)
            
            # Create metadata
            metadata = {
                "offer_id": offer_id,
                "dataset_name": self.dataset_name,
                "preparation_method": "gas_concentration",
                "features": sensor_cols,
                "target": "concentration",
                "target_readable": "concentration_level",
                "target_encoded": "concentration_encoded",
                "samples": len(combined_df),
                "gases": list(gas_datasets.keys()),
                "gas_datasets": gas_datasets,
                "file_paths": {
                    "combined": output_path,
                    **{gas_name: info["path"] for gas_name, info in gas_datasets.items()}
                }
            }
            
            # Save metadata
            metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "success": True,
                "dataset_path": output_path,
                "gas_dataset_paths": {gas_name: info["path"] for gas_name, info in gas_datasets.items()},
                "metadata_path": metadata_path,
                "metadata": metadata
            }
        else:
            return {
                "success": False,
                "error": "Gas type or concentration information not found in dataset"
            }
    
    def _prepare_drift_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for sensor drift detection offer.
        
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
        sensor_cols = [col for col in df.columns if col.startswith("S") and "_F" in col]
        
        # Prepare the dataset for drift detection
        if "batch_id" in df.columns:
            # Create a dataset with batch information
            prepared_df = df[sensor_cols + ["batch_id", "gas_type", "gas_name", "concentration"]].copy()
            
            # Add time information if available
            if "time_stamp" in df.columns:
                prepared_df["time_stamp"] = df["time_stamp"]
            
            if "normalized_time" in df.columns:
                prepared_df["normalized_time"] = df["normalized_time"]
            
            if "drift_indicator" in df.columns:
                prepared_df["drift_indicator"] = df["drift_indicator"]
            
            # Save prepared dataset
            output_dir = os.path.join(self.processed_dir, "offers")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
            prepared_df.to_csv(output_path, index=False)
            
            # Create metadata
            metadata = {
                "offer_id": offer_id,
                "dataset_name": self.dataset_name,
                "preparation_method": "drift_detection",
                "features": sensor_cols,
                "batch_column": "batch_id",
                "samples": len(prepared_df),
                "batches": len(prepared_df["batch_id"].unique()),
                "batch_distribution": prepared_df["batch_id"].value_counts().to_dict(),
                "file_path": output_path
            }
            
            # Add drift information if available
            if "drift_indicator" in prepared_df.columns:
                metadata["drift_column"] = "drift_indicator"
                metadata["drift_distribution"] = {
                    "early_measurements": int((prepared_df["drift_indicator"] == 0).sum()),
                    "late_measurements": int((prepared_df["drift_indicator"] == 1).sum())
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
        else:
            return {
                "success": False,
                "error": "Batch information not found in dataset"
            }
    
    def _prepare_sensor_fusion(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for sensor fusion offer.
        
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
        sensor_cols = [col for col in df.columns if col.startswith("S") and "_F" in col]
        
        # Get sensor group columns
        sensor_group_cols = [col for col in df.columns if col.startswith("sensor_group_") and col.endswith("_avg")]
        
        # Load sensor groups
        groups_path = os.path.join(self.metadata_dir, "sensor_groups.json")
        sensor_groups = {}
        
        if os.path.exists(groups_path):
            with open(groups_path, 'r') as f:
                sensor_groups = json.load(f)
        
        # Prepare the dataset for sensor fusion
        if "combined_target" in df.columns and "combined_target_encoded" in df.columns:
            # Create a dataset with individual sensors and sensor groups
            prepared_df = df[sensor_cols + sensor_group_cols + ["gas_type", "gas_name", "concentration", "combined_target", "combined_target_encoded"]].copy()
            
            # Save prepared dataset
            output_dir = os.path.join(self.processed_dir, "offers")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
            prepared_df.to_csv(output_path, index=False)
            
            # Create metadata
            metadata = {
                "offer_id": offer_id,
                "dataset_name": self.dataset_name,
                "preparation_method": "sensor_fusion",
                "individual_sensors": sensor_cols,
                "sensor_groups": sensor_group_cols,
                "sensor_group_details": sensor_groups,
                "target": "combined_target",
                "target_encoded": "combined_target_encoded",
                "samples": len(prepared_df),
                "classes": len(prepared_df["combined_target"].unique()),
                "class_distribution": prepared_df["combined_target"].value_counts().to_dict(),
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
        else:
            return {
                "success": False,
                "error": "Combined target information not found in dataset"
            }
    
    def _prepare_anomaly_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for anomaly detection offer.
        
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
        sensor_cols = [col for col in df.columns if col.startswith("S") and "_F" in col]
        
        # Create anomaly indicator
        # An anomaly is defined as a rare gas type or concentration
        if "gas_type" in df.columns and "concentration" in df.columns:
            # Get gas type and concentration counts
            gas_counts = df["gas_type"].value_counts()
            conc_counts = df["concentration"].value_counts()
            
            # Define rare gases (bottom 20% by frequency)
            rare_gases = gas_counts[gas_counts < gas_counts.quantile(0.2)].index.tolist()
            
            # Define rare concentrations (bottom 20% by frequency)
            rare_concentrations = conc_counts[conc_counts < conc_counts.quantile(0.2)].index.tolist()
            
            # Create anomaly indicator
            df["anomaly"] = ((df["gas_type"].isin(rare_gases)) | (df["concentration"].isin(rare_concentrations))).astype(int)
            
            # Create a balanced dataset for anomaly detection
            normal_samples = df[df["anomaly"] == 0].sample(
                n=min(5000, (df["anomaly"] == 0).sum()),
                random_state=42
            )
            
            anomaly_samples = df[df["anomaly"] == 1]
            
            balanced_df = pd.concat([normal_samples, anomaly_samples])
            
            # Select columns for the prepared dataset
            prepared_df = balanced_df[sensor_cols + ["gas_type", "gas_name", "concentration", "concentration_level", "anomaly"]].copy()
            
            # Save prepared dataset
            output_dir = os.path.join(self.processed_dir, "offers")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
            prepared_df.to_csv(output_path, index=False)
            
            # Create metadata
            metadata = {
                "offer_id": offer_id,
                "dataset_name": self.dataset_name,
                "preparation_method": "anomaly_detection",
                "features": sensor_cols,
                "target": "anomaly",
                "samples": len(prepared_df),
                "normal_samples": int((prepared_df["anomaly"] == 0).sum()),
                "anomaly_samples": int(prepared_df["anomaly"].sum()),
                "rare_gases": rare_gases,
                "rare_concentrations": rare_concentrations,
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
        else:
            return {
                "success": False,
                "error": "Gas type or concentration information not found in dataset"
            }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create Gas Sensor Array dataset connector
    connector = GasSensorDatasetConnector()
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        data_dir="path/to/gas_sensor_data"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("gas_detection_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
