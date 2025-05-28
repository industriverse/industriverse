"""
SECOM Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for the SECOM
semiconductor manufacturing dataset, supporting MCP/A2A integration.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from .dataset_connector_base import DatasetConnectorBase

logger = logging.getLogger(__name__)

class SECOMDatasetConnector(DatasetConnectorBase):
    """
    Connector for SECOM Semiconductor Manufacturing Dataset.
    
    This connector provides protocol-native ingestion, validation, and
    transformation for the SECOM dataset, with support for semiconductor
    manufacturing quality control use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "secom-connector",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the SECOM dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["semiconductor", "manufacturing", "quality_control"],
            "feature_selection_threshold": 0.05,  # p-value threshold for feature selection
            "missing_value_threshold": 0.3,  # Maximum ratio of missing values allowed per feature
            "outlier_detection": {
                "method": "iqr",  # interquartile range method
                "factor": 1.5     # IQR factor for outlier detection
            }
        }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name="secom",
            dataset_type="timeseries",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.features_dir = os.path.join(self.processed_dir, "features")
        self.labels_dir = os.path.join(self.processed_dir, "labels")
        self.models_dir = os.path.join(self.processed_dir, "models")
        
        os.makedirs(self.features_dir, exist_ok=True)
        os.makedirs(self.labels_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("Initialized SECOM dataset connector")
    
    def ingest_dataset(
        self,
        features_file: str,
        labels_file: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the complete SECOM dataset.
        
        Args:
            features_file: Path to the features data file
            labels_file: Path to the labels data file
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
                            "features": features_file,
                            "labels": labels_file
                        }
                    }
                )
            
            # Ingest features data
            features_result = self.ingest_data(
                source_path=features_file,
                validate=validate,
                transform=False,  # We'll transform after merging
                emit_events=False
            )
            
            # Ingest labels data
            labels_result = self.ingest_data(
                source_path=labels_file,
                validate=validate,
                transform=False,  # We'll transform after merging
                emit_events=False
            )
            
            # Process the complete dataset
            if features_result["success"] and labels_result["success"]:
                merged_result = self._process_complete_dataset(
                    features_path=features_result["raw_path"],
                    labels_path=labels_result["raw_path"],
                    transform=transform
                )
            else:
                merged_result = {
                    "success": False,
                    "error": "Failed to ingest features or labels data"
                }
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "success": features_result["success"] and labels_result["success"] and merged_result["success"],
                "status": "dataset_ingestion_completed" if merged_result["success"] else "dataset_ingestion_failed",
                "components": {
                    "features": features_result,
                    "labels": labels_result,
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
        if source_path.endswith('.data'):
            # SECOM dataset uses space-delimited files with .data extension
            if "secom_labels" in source_path.lower():
                # Labels file has two columns: label and timestamp
                df = pd.read_csv(source_path, header=None, sep=' ')
                if len(df.columns) >= 2:
                    df.columns = ["label", "timestamp"]
                else:
                    df.columns = ["label"]
            else:
                # Features file has 590 columns with no header
                df = pd.read_csv(source_path, header=None, sep=' ')
                # Name columns as "feature_1", "feature_2", etc.
                df.columns = [f"feature_{i+1}" for i in range(len(df.columns))]
        elif source_path.endswith('.csv'):
            df = pd.read_csv(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        return df
    
    def _validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the SECOM dataset.
        
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
        
        # Check for expected columns in labels data
        if "label" in data.columns:
            # This is labels data
            if not pd.api.types.is_numeric_dtype(data["label"]):
                errors.append("Column 'label' is not numeric")
            
            # Check for invalid label values (should be -1 or 1)
            valid_labels = set([-1, 1])
            invalid_labels = set(data["label"].dropna().unique()) - valid_labels
            if invalid_labels:
                errors.append(f"Invalid label values found: {invalid_labels}")
        
        # Check for expected columns in features data
        elif "feature_1" in data.columns:
            # This is features data
            # Check for numeric data types
            non_numeric_cols = []
            for col in data.columns:
                if not pd.api.types.is_numeric_dtype(data[col]):
                    non_numeric_cols.append(col)
            
            if non_numeric_cols:
                errors.append(f"Non-numeric columns found: {non_numeric_cols}")
        
        # Check for missing values
        missing_count = data.isna().sum().sum()
        missing_ratio = missing_count / (data.shape[0] * data.shape[1])
        
        if missing_count > 0:
            if missing_ratio > 0.5:
                errors.append(f"Data contains excessive missing values: {missing_count} ({missing_ratio:.2%})")
            else:
                warnings.append(f"Data contains {missing_count} missing values ({missing_ratio:.2%})")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _process_complete_dataset(
        self,
        features_path: str,
        labels_path: str,
        transform: bool = True
    ) -> Dict[str, Any]:
        """
        Process the complete dataset after individual files are ingested.
        
        Args:
            features_path: Path to the raw features data
            labels_path: Path to the raw labels data
            transform: Whether to transform the data
            
        Returns:
            Processing result information
        """
        try:
            # Load raw data
            features_df = pd.read_csv(features_path)
            labels_df = pd.read_csv(labels_path)
            
            # Ensure the number of rows match
            if len(features_df) != len(labels_df):
                logger.error(f"Row count mismatch: features={len(features_df)}, labels={len(labels_df)}")
                return {
                    "success": False,
                    "error": f"Row count mismatch: features={len(features_df)}, labels={len(labels_df)}"
                }
            
            # Merge features and labels
            merged_df = features_df.copy()
            merged_df["label"] = labels_df["label"]
            
            if "timestamp" in labels_df.columns:
                merged_df["timestamp"] = labels_df["timestamp"]
            
            # Save merged raw data
            merged_raw_path = os.path.join(self.raw_dir, "secom_merged_raw.csv")
            merged_df.to_csv(merged_raw_path, index=False)
            
            # Transform data if requested
            if transform:
                transformed_df = self._transform_data(merged_df)
                
                # Save transformed data
                transformed_path = os.path.join(self.processed_dir, "secom_transformed.csv")
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
        Transform the SECOM dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Separate features and labels
        label_cols = ["label"]
        if "timestamp" in df.columns:
            label_cols.append("timestamp")
        
        features = df.drop(columns=label_cols)
        labels = df[label_cols]
        
        # 1. Handle missing values
        # Calculate missing value ratio for each feature
        missing_ratio = features.isna().mean()
        
        # Remove features with too many missing values
        missing_threshold = self.config.get("missing_value_threshold", 0.3)
        high_missing_cols = missing_ratio[missing_ratio > missing_threshold].index.tolist()
        
        if high_missing_cols:
            logger.info(f"Removing {len(high_missing_cols)} features with >={missing_threshold:.0%} missing values")
            features = features.drop(columns=high_missing_cols)
        
        # Impute remaining missing values
        imputer = SimpleImputer(strategy='median')
        features_imputed = pd.DataFrame(
            imputer.fit_transform(features),
            columns=features.columns
        )
        
        # 2. Handle outliers
        outlier_method = self.config.get("outlier_detection", {}).get("method", "iqr")
        
        if outlier_method == "iqr":
            # Use IQR method for outlier detection
            factor = self.config.get("outlier_detection", {}).get("factor", 1.5)
            
            for col in features_imputed.columns:
                q1 = features_imputed[col].quantile(0.25)
                q3 = features_imputed[col].quantile(0.75)
                iqr = q3 - q1
                
                lower_bound = q1 - factor * iqr
                upper_bound = q3 + factor * iqr
                
                # Cap outliers
                features_imputed[col] = features_imputed[col].clip(lower=lower_bound, upper=upper_bound)
        
        # 3. Feature selection
        # We'll use correlation with the target for simple feature selection
        if "label" in labels.columns:
            # Add label back for correlation calculation
            temp_df = features_imputed.copy()
            temp_df["label"] = labels["label"]
            
            # Calculate correlation with target
            correlations = temp_df.corr()["label"].drop("label")
            
            # Select features with absolute correlation above threshold
            threshold = self.config.get("feature_selection_threshold", 0.05)
            selected_features = correlations[abs(correlations) > threshold].index.tolist()
            
            if selected_features:
                logger.info(f"Selected {len(selected_features)} features with correlation > {threshold}")
                features_selected = features_imputed[selected_features]
            else:
                # If no features meet the threshold, keep all
                logger.warning(f"No features met correlation threshold {threshold}, keeping all")
                features_selected = features_imputed
        else:
            # If no label column, keep all features
            features_selected = features_imputed
        
        # 4. Standardize features
        scaler = StandardScaler()
        features_scaled = pd.DataFrame(
            scaler.fit_transform(features_selected),
            columns=features_selected.columns
        )
        
        # Save preprocessing objects for later use
        preprocessing = {
            "imputer": imputer,
            "scaler": scaler,
            "selected_features": features_selected.columns.tolist(),
            "removed_features": high_missing_cols
        }
        
        preprocessing_path = os.path.join(self.models_dir, "preprocessing.pkl")
        import pickle
        with open(preprocessing_path, 'wb') as f:
            pickle.dump(preprocessing, f)
        
        # Combine transformed features with labels
        result = pd.concat([features_scaled, labels], axis=1)
        
        # Add metadata columns
        result["missing_value_count"] = features.isna().sum(axis=1)
        result["missing_value_ratio"] = features.isna().mean(axis=1)
        
        # Add class balance information
        if "label" in result.columns:
            # Convert -1 to 0 for easier interpretation
            result["class"] = result["label"].replace({-1: 0, 1: 1})
        
        return result
    
    def _create_dataset_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Create a summary of the dataset.
        
        Args:
            data: Processed dataset
            
        Returns:
            Dataset summary dictionary
        """
        summary = {
            "dataset_name": self.dataset_name,
            "samples": len(data),
            "features": len(data.columns) - (1 if "label" in data.columns else 0) - (1 if "timestamp" in data.columns else 0),
            "missing_values": {
                "total": int(data["missing_value_count"].sum()),
                "average_per_sample": float(data["missing_value_count"].mean())
            }
        }
        
        # Add class distribution if available
        if "label" in data.columns:
            label_counts = data["label"].value_counts().to_dict()
            
            # Convert keys to strings for JSON serialization
            label_counts = {str(k): int(v) for k, v in label_counts.items()}
            
            summary["class_distribution"] = label_counts
            
            # Calculate class balance
            total = sum(label_counts.values())
            class_balance = {k: v / total for k, v in label_counts.items()}
            
            summary["class_balance"] = {k: float(v) for k, v in class_balance.items()}
        
        # Add feature importance if available
        if "label" in data.columns:
            # Use correlation as a simple measure of feature importance
            feature_cols = [col for col in data.columns if col.startswith("feature_")]
            
            if feature_cols:
                correlations = data[feature_cols + ["label"]].corr()["label"].drop("label")
                
                # Get top 10 features by absolute correlation
                top_features = correlations.abs().sort_values(ascending=False).head(10)
                
                feature_importance = {}
                for feature in top_features.index:
                    feature_importance[feature] = float(correlations[feature])
                
                summary["feature_importance"] = feature_importance
        
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
                "semiconductor_quality": self._prepare_quality_control,
                "fault_detection": self._prepare_fault_detection,
                "anomaly_detection": self._prepare_anomaly_detection,
                "process_monitoring": self._prepare_process_monitoring,
                "manufacturing_analytics": self._prepare_manufacturing_analytics
            }
            
            # Find the appropriate preparation method
            preparation_method = None
            for offer_prefix, method in offer_mappings.items():
                if offer_id.startswith(offer_prefix):
                    preparation_method = method
                    break
            
            # Use default method if no specific method found
            if preparation_method is None:
                preparation_method = self._prepare_quality_control
            
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
    
    def _prepare_quality_control(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for semiconductor quality control offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed data
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.csv')]
        if not processed_files:
            return {"success": False, "error": "No processed data found"}
        
        latest_file = sorted(processed_files)[-1]
        processed_path = os.path.join(self.processed_dir, latest_file)
        
        # Load the data
        df = pd.read_csv(processed_path)
        
        # Ensure we have the label column
        if "label" not in df.columns:
            return {"success": False, "error": "Label column not found in processed data"}
        
        # Prepare the dataset
        # For quality control, we want to predict defects (label=1) vs. non-defects (label=-1)
        prepared_df = df.copy()
        
        # Convert labels to 0/1 for easier interpretation
        prepared_df["defect"] = prepared_df["label"].replace({-1: 0, 1: 1})
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "quality_control",
            "features": [col for col in prepared_df.columns if col.startswith("feature_")],
            "target": "defect",
            "samples": len(prepared_df),
            "defect_samples": int(prepared_df["defect"].sum()),
            "non_defect_samples": int((prepared_df["defect"] == 0).sum()),
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
        Prepare dataset for semiconductor fault detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed data
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.csv')]
        if not processed_files:
            return {"success": False, "error": "No processed data found"}
        
        latest_file = sorted(processed_files)[-1]
        processed_path = os.path.join(self.processed_dir, latest_file)
        
        # Load the data
        df = pd.read_csv(processed_path)
        
        # Ensure we have the label column
        if "label" not in df.columns:
            return {"success": False, "error": "Label column not found in processed data"}
        
        # Prepare the dataset
        # For fault detection, we want to create a more balanced dataset
        prepared_df = df.copy()
        
        # Convert labels to 0/1 for easier interpretation
        prepared_df["fault"] = prepared_df["label"].replace({-1: 0, 1: 1})
        
        # Create a balanced dataset
        fault_samples = prepared_df[prepared_df["fault"] == 1]
        non_fault_samples = prepared_df[prepared_df["fault"] == 0].sample(
            n=min(len(fault_samples) * 2, (prepared_df["fault"] == 0).sum()),
            random_state=42
        )
        
        balanced_df = pd.concat([fault_samples, non_fault_samples])
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        balanced_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "fault_detection",
            "features": [col for col in balanced_df.columns if col.startswith("feature_")],
            "target": "fault",
            "samples": len(balanced_df),
            "fault_samples": int(balanced_df["fault"].sum()),
            "non_fault_samples": int((balanced_df["fault"] == 0).sum()),
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
        Prepare dataset for semiconductor anomaly detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed data
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.csv')]
        if not processed_files:
            return {"success": False, "error": "No processed data found"}
        
        latest_file = sorted(processed_files)[-1]
        processed_path = os.path.join(self.processed_dir, latest_file)
        
        # Load the data
        df = pd.read_csv(processed_path)
        
        # Ensure we have the label column
        if "label" not in df.columns:
            return {"success": False, "error": "Label column not found in processed data"}
        
        # Prepare the dataset
        # For anomaly detection, we treat defects as anomalies
        prepared_df = df.copy()
        
        # Convert labels to 0/1 for easier interpretation
        prepared_df["anomaly"] = prepared_df["label"].replace({-1: 0, 1: 1})
        
        # Select only feature columns and anomaly label
        feature_cols = [col for col in prepared_df.columns if col.startswith("feature_")]
        selected_cols = feature_cols + ["anomaly"]
        
        prepared_df = prepared_df[selected_cols]
        
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
            "features": feature_cols,
            "target": "anomaly",
            "samples": len(prepared_df),
            "anomaly_samples": int(prepared_df["anomaly"].sum()),
            "normal_samples": int((prepared_df["anomaly"] == 0).sum()),
            "anomaly_ratio": float(prepared_df["anomaly"].mean()),
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
    
    def _prepare_process_monitoring(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for semiconductor process monitoring offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed data
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.csv')]
        if not processed_files:
            return {"success": False, "error": "No processed data found"}
        
        latest_file = sorted(processed_files)[-1]
        processed_path = os.path.join(self.processed_dir, latest_file)
        
        # Load the data
        df = pd.read_csv(processed_path)
        
        # Prepare the dataset
        # For process monitoring, we want to include time information if available
        prepared_df = df.copy()
        
        # Add sequential process ID if timestamp not available
        if "timestamp" not in prepared_df.columns:
            prepared_df["process_id"] = range(1, len(prepared_df) + 1)
        
        # Calculate moving averages for key features
        feature_cols = [col for col in prepared_df.columns if col.startswith("feature_")]
        
        # Select top features by variance
        variances = prepared_df[feature_cols].var()
        top_features = variances.sort_values(ascending=False).head(20).index.tolist()
        
        # Calculate moving averages for top features
        window_size = 10
        for feature in top_features:
            prepared_df[f"{feature}_ma{window_size}"] = prepared_df[feature].rolling(window=window_size, min_periods=1).mean()
        
        # Add control limits
        for feature in top_features:
            mean = prepared_df[feature].mean()
            std = prepared_df[feature].std()
            
            prepared_df[f"{feature}_ucl"] = mean + 3 * std  # Upper control limit
            prepared_df[f"{feature}_lcl"] = mean - 3 * std  # Lower control limit
            prepared_df[f"{feature}_out_of_control"] = (
                (prepared_df[feature] > prepared_df[f"{feature}_ucl"]) | 
                (prepared_df[feature] < prepared_df[f"{feature}_lcl"])
            ).astype(int)
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "process_monitoring",
            "features": feature_cols,
            "top_features": top_features,
            "control_features": [f"{feature}_out_of_control" for feature in top_features],
            "samples": len(prepared_df),
            "out_of_control_samples": sum(prepared_df[f"{feature}_out_of_control"].sum() for feature in top_features),
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
    
    def _prepare_manufacturing_analytics(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for semiconductor manufacturing analytics offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the latest processed data
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.csv')]
        if not processed_files:
            return {"success": False, "error": "No processed data found"}
        
        latest_file = sorted(processed_files)[-1]
        processed_path = os.path.join(self.processed_dir, latest_file)
        
        # Load the data
        df = pd.read_csv(processed_path)
        
        # Ensure we have the label column
        if "label" not in df.columns:
            return {"success": False, "error": "Label column not found in processed data"}
        
        # Prepare the dataset
        # For manufacturing analytics, we want to include feature importance and correlations
        prepared_df = df.copy()
        
        # Convert labels to 0/1 for easier interpretation
        prepared_df["defect"] = prepared_df["label"].replace({-1: 0, 1: 1})
        
        # Calculate feature importance using correlation
        feature_cols = [col for col in prepared_df.columns if col.startswith("feature_")]
        
        # Calculate correlation with target
        correlations = prepared_df[feature_cols + ["defect"]].corr()["defect"].drop("defect")
        
        # Get top features by absolute correlation
        top_features = correlations.abs().sort_values(ascending=False).head(30).index.tolist()
        
        # Create correlation matrix for top features
        top_corr = prepared_df[top_features].corr()
        
        # Save correlation matrix
        corr_path = os.path.join(self.processed_dir, "offers", f"{offer_id}_correlation.csv")
        os.makedirs(os.path.dirname(corr_path), exist_ok=True)
        top_corr.to_csv(corr_path)
        
        # Create feature importance file
        importance_df = pd.DataFrame({
            "feature": correlations.index,
            "importance": correlations.abs(),
            "correlation": correlations
        }).sort_values("importance", ascending=False)
        
        importance_path = os.path.join(self.processed_dir, "offers", f"{offer_id}_feature_importance.csv")
        importance_df.to_csv(importance_path, index=False)
        
        # Prepare final dataset with top features
        final_df = prepared_df[top_features + ["defect"]]
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        final_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "manufacturing_analytics",
            "features": top_features,
            "target": "defect",
            "samples": len(final_df),
            "defect_samples": int(final_df["defect"].sum()),
            "non_defect_samples": int((final_df["defect"] == 0).sum()),
            "top_positive_correlated_features": correlations.sort_values(ascending=False).head(5).index.tolist(),
            "top_negative_correlated_features": correlations.sort_values().head(5).index.tolist(),
            "file_paths": {
                "dataset": output_path,
                "correlation_matrix": corr_path,
                "feature_importance": importance_path
            }
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "correlation_path": corr_path,
            "importance_path": importance_path,
            "metadata_path": metadata_path,
            "metadata": metadata
        }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create SECOM dataset connector
    connector = SECOMDatasetConnector()
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        features_file="path/to/secom.data",
        labels_file="path/to/secom_labels.data"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("semiconductor_quality_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
