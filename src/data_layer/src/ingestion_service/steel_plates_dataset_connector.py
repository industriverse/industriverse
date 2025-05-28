"""
Steel Plates Faults Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for the Steel Plates Faults
dataset, supporting MCP/A2A integration for manufacturing quality control.
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

class SteelPlatesDatasetConnector(DatasetConnectorBase):
    """
    Connector for Steel Plates Faults Dataset.
    
    This connector provides protocol-native ingestion, validation, and
    transformation for the Steel Plates Faults dataset, with support
    for manufacturing quality control use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "steel-plates-connector",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the Steel Plates dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "steel", "quality_control"],
            "fault_types": [
                "Pastry", "Z_Scratch", "K_Scratch", "Stains", 
                "Dirtiness", "Bumps", "Other_Faults"
            ],
            "feature_descriptions": {
                "X_Minimum": "Minimum X position of the fault",
                "X_Maximum": "Maximum X position of the fault",
                "Y_Minimum": "Minimum Y position of the fault",
                "Y_Maximum": "Maximum Y position of the fault",
                "Pixels_Areas": "Area of the fault in pixels",
                "X_Perimeter": "Perimeter of the fault in X direction",
                "Y_Perimeter": "Perimeter of the fault in Y direction",
                "Sum_of_Luminosity": "Sum of luminosity values in the fault area",
                "Minimum_of_Luminosity": "Minimum luminosity value in the fault area",
                "Maximum_of_Luminosity": "Maximum luminosity value in the fault area",
                "Length_of_Conveyer": "Length of the conveyer belt",
                "TypeOfSteel_A300": "Steel type A300 indicator",
                "TypeOfSteel_A400": "Steel type A400 indicator",
                "Steel_Plate_Thickness": "Thickness of the steel plate",
                "Edges_Index": "Index of edges in the fault",
                "Empty_Index": "Index of empty areas",
                "Square_Index": "Index of square-shaped faults",
                "Outside_X_Index": "Index of outside X position",
                "Edges_X_Index": "Index of edges in X direction",
                "Edges_Y_Index": "Index of edges in Y direction",
                "Outside_Global_Index": "Global index of outside position",
                "LogOfAreas": "Logarithm of the fault area",
                "Log_X_Index": "Logarithm of X index",
                "Log_Y_Index": "Logarithm of Y index",
                "Orientation_Index": "Index of fault orientation",
                "Luminosity_Index": "Index of luminosity",
                "SigmoidOfAreas": "Sigmoid function of the fault area"
            }
        }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name="steel_plates_faults",
            dataset_type="tabular",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.binary_dir = os.path.join(self.processed_dir, "binary")
        self.multiclass_dir = os.path.join(self.processed_dir, "multiclass")
        self.models_dir = os.path.join(self.processed_dir, "models")
        
        os.makedirs(self.binary_dir, exist_ok=True)
        os.makedirs(self.multiclass_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("Initialized Steel Plates Faults dataset connector")
    
    def ingest_dataset(
        self,
        data_file: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the Steel Plates Faults dataset.
        
        Args:
            data_file: Path to the data file
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
                            "data": data_file
                        }
                    }
                )
            
            # Ingest data
            result = self.ingest_data(
                source_path=data_file,
                validate=validate,
                transform=transform,
                emit_events=False
            )
            
            # Process the dataset for different use cases
            if transform and result["success"]:
                self._process_dataset_variants(result["processed_path"])
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
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
            return {
                "success": result["success"],
                "status": "dataset_ingestion_completed" if result["success"] else "dataset_ingestion_failed",
                "raw_path": result.get("raw_path"),
                "processed_path": result.get("processed_path"),
                "statistics": self.metadata["statistics"] if "statistics" in self.metadata else {},
                "duration": duration
            }
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
        if source_path.endswith('.csv'):
            # Try to detect delimiter
            with open(source_path, 'r') as f:
                first_line = f.readline()
                if ',' in first_line:
                    df = pd.read_csv(source_path)
                elif ';' in first_line:
                    df = pd.read_csv(source_path, sep=';')
                elif '\t' in first_line:
                    df = pd.read_csv(source_path, sep='\t')
                else:
                    # Default to comma
                    df = pd.read_csv(source_path)
        elif source_path.endswith('.data') or source_path.endswith('.txt'):
            # Try to detect delimiter
            with open(source_path, 'r') as f:
                first_line = f.readline()
                if ',' in first_line:
                    df = pd.read_csv(source_path, header=None)
                elif ';' in first_line:
                    df = pd.read_csv(source_path, sep=';', header=None)
                elif '\t' in first_line:
                    df = pd.read_csv(source_path, sep='\t', header=None)
                else:
                    # Default to whitespace
                    df = pd.read_csv(source_path, delim_whitespace=True, header=None)
            
            # Check if this is the Steel Plates Faults dataset
            if df.shape[1] == 34:  # 27 features + 7 fault type columns
                # The dataset has 27 features and 7 fault type columns
                feature_names = [
                    "X_Minimum", "X_Maximum", "Y_Minimum", "Y_Maximum", 
                    "Pixels_Areas", "X_Perimeter", "Y_Perimeter", 
                    "Sum_of_Luminosity", "Minimum_of_Luminosity", "Maximum_of_Luminosity", 
                    "Length_of_Conveyer", "TypeOfSteel_A300", "TypeOfSteel_A400", 
                    "Steel_Plate_Thickness", "Edges_Index", "Empty_Index", 
                    "Square_Index", "Outside_X_Index", "Edges_X_Index", 
                    "Edges_Y_Index", "Outside_Global_Index", "LogOfAreas", 
                    "Log_X_Index", "Log_Y_Index", "Orientation_Index", 
                    "Luminosity_Index", "SigmoidOfAreas"
                ]
                
                fault_types = self.config.get("fault_types", [
                    "Pastry", "Z_Scratch", "K_Scratch", "Stains", 
                    "Dirtiness", "Bumps", "Other_Faults"
                ])
                
                # Assign column names
                df.columns = feature_names + fault_types
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        return df
    
    def _validate_data(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the Steel Plates Faults dataset.
        
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
        
        # Check for expected fault type columns
        fault_types = self.config.get("fault_types", [
            "Pastry", "Z_Scratch", "K_Scratch", "Stains", 
            "Dirtiness", "Bumps", "Other_Faults"
        ])
        
        missing_fault_types = [ft for ft in fault_types if ft not in data.columns]
        if missing_fault_types:
            warnings.append(f"Missing fault type columns: {missing_fault_types}")
        
        # Check for expected feature columns
        expected_features = [
            "X_Minimum", "X_Maximum", "Y_Minimum", "Y_Maximum", 
            "Pixels_Areas", "X_Perimeter", "Y_Perimeter"
        ]
        
        missing_features = [feat for feat in expected_features if feat not in data.columns]
        if missing_features:
            warnings.append(f"Missing expected feature columns: {missing_features}")
        
        # Check for numeric data types in feature columns
        non_numeric_cols = []
        for col in data.columns:
            if col not in fault_types and not pd.api.types.is_numeric_dtype(data[col]):
                non_numeric_cols.append(col)
        
        if non_numeric_cols:
            errors.append(f"Non-numeric feature columns found: {non_numeric_cols}")
        
        # Check for binary values in fault type columns
        non_binary_fault_cols = []
        for col in fault_types:
            if col in data.columns:
                unique_values = data[col].unique()
                if not all(val in [0, 1] for val in unique_values):
                    non_binary_fault_cols.append(col)
        
        if non_binary_fault_cols:
            errors.append(f"Non-binary values found in fault type columns: {non_binary_fault_cols}")
        
        # Check for missing values
        missing_count = data.isna().sum().sum()
        if missing_count > 0:
            warnings.append(f"Data contains {missing_count} missing values")
        
        # Check for duplicate rows
        duplicate_count = data.duplicated().sum()
        if duplicate_count > 0:
            warnings.append(f"Data contains {duplicate_count} duplicate rows")
        
        # Check for class imbalance
        if all(ft in data.columns for ft in fault_types):
            fault_counts = {ft: int(data[ft].sum()) for ft in fault_types}
            total_faults = sum(fault_counts.values())
            
            if total_faults == 0:
                errors.append("No faults found in the dataset")
            else:
                # Check for severe class imbalance
                min_fault = min(fault_counts.values())
                max_fault = max(fault_counts.values())
                
                if min_fault == 0:
                    warnings.append(f"Some fault types have zero occurrences: {[ft for ft, count in fault_counts.items() if count == 0]}")
                
                if min_fault > 0 and max_fault / min_fault > 10:
                    warnings.append(f"Severe class imbalance detected: ratio of most common to least common fault is {max_fault / min_fault:.1f}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the Steel Plates Faults dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Get fault type columns
        fault_types = self.config.get("fault_types", [
            "Pastry", "Z_Scratch", "K_Scratch", "Stains", 
            "Dirtiness", "Bumps", "Other_Faults"
        ])
        
        # Filter to fault types that exist in the data
        fault_types = [ft for ft in fault_types if ft in df.columns]
        
        # Get feature columns (all columns that are not fault types)
        feature_cols = [col for col in df.columns if col not in fault_types]
        
        # Handle missing values in feature columns
        for col in feature_cols:
            if df[col].isna().any():
                # Fill missing values with median
                df[col] = df[col].fillna(df[col].median())
        
        # Create a single fault type column for multi-class classification
        if fault_types:
            # Check if each row has exactly one fault type
            fault_sums = df[fault_types].sum(axis=1)
            
            if (fault_sums == 1).all():
                # Each row has exactly one fault type, create a single column
                df['fault_type'] = 'None'
                for ft in fault_types:
                    df.loc[df[ft] == 1, 'fault_type'] = ft
            else:
                # Some rows have multiple or no fault types
                # For rows with multiple faults, use the first one
                df['fault_type'] = 'None'
                for ft in fault_types:
                    mask = (df[ft] == 1) & (df['fault_type'] == 'None')
                    df.loc[mask, 'fault_type'] = ft
                
                # For rows with no faults, mark as 'None'
                # (already done by default)
            
            # Create a binary fault indicator (1 if any fault, 0 if no fault)
            df['has_fault'] = (fault_sums > 0).astype(int)
        
        # Standardize numeric features
        scaler = StandardScaler()
        numeric_cols = [col for col in feature_cols if pd.api.types.is_numeric_dtype(df[col])]
        
        if numeric_cols:
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            
            # Save the scaler for later use
            import pickle
            scaler_path = os.path.join(self.models_dir, "feature_scaler.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
        
        # Encode the fault_type column
        if 'fault_type' in df.columns:
            encoder = LabelEncoder()
            df['fault_type_encoded'] = encoder.fit_transform(df['fault_type'])
            
            # Save the encoder for later use
            import pickle
            encoder_path = os.path.join(self.models_dir, "fault_type_encoder.pkl")
            with open(encoder_path, 'wb') as f:
                pickle.dump(encoder, f)
            
            # Create a mapping from encoded values to fault types
            fault_type_mapping = {i: label for i, label in enumerate(encoder.classes_)}
            
            # Save the mapping
            mapping_path = os.path.join(self.metadata_dir, "fault_type_mapping.json")
            with open(mapping_path, 'w') as f:
                json.dump(fault_type_mapping, f, indent=2)
        
        return df
    
    def _process_dataset_variants(self, processed_path: str) -> Dict[str, str]:
        """
        Process the dataset into different variants for various use cases.
        
        Args:
            processed_path: Path to the processed dataset
            
        Returns:
            Dictionary of output file paths
        """
        try:
            # Load processed data
            df = pd.read_csv(processed_path)
            
            # Get fault type columns
            fault_types = self.config.get("fault_types", [
                "Pastry", "Z_Scratch", "K_Scratch", "Stains", 
                "Dirtiness", "Bumps", "Other_Faults"
            ])
            
            # Filter to fault types that exist in the data
            fault_types = [ft for ft in fault_types if ft in df.columns]
            
            # Create binary classification dataset
            if 'has_fault' in df.columns:
                binary_df = df.drop(columns=fault_types)
                binary_path = os.path.join(self.binary_dir, "steel_plates_binary.csv")
                binary_df.to_csv(binary_path, index=False)
            
            # Create multi-class classification dataset
            if 'fault_type' in df.columns and 'fault_type_encoded' in df.columns:
                multiclass_df = df.drop(columns=fault_types)
                multiclass_path = os.path.join(self.multiclass_dir, "steel_plates_multiclass.csv")
                multiclass_df.to_csv(multiclass_path, index=False)
            
            # Create a dataset summary
            summary = {
                "dataset_name": self.dataset_name,
                "samples": len(df),
                "features": len([col for col in df.columns if col not in fault_types and col not in ['fault_type', 'fault_type_encoded', 'has_fault']]),
                "fault_types": fault_types,
                "fault_distribution": {ft: int(df[ft].sum()) for ft in fault_types if ft in df.columns},
                "binary_classification": {
                    "positive_samples": int(df['has_fault'].sum()) if 'has_fault' in df.columns else 0,
                    "negative_samples": int((df['has_fault'] == 0).sum()) if 'has_fault' in df.columns else 0
                },
                "multiclass_classification": {
                    "classes": list(df['fault_type'].unique()) if 'fault_type' in df.columns else [],
                    "class_distribution": df['fault_type'].value_counts().to_dict() if 'fault_type' in df.columns else {}
                }
            }
            
            # Save summary
            summary_path = os.path.join(self.metadata_dir, "dataset_summary.json")
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            # Update metadata with summary
            self.metadata["dataset_summary"] = summary
            self._save_metadata()
            
            logger.info(f"Processed dataset variants and saved summary to {summary_path}")
            
            return {
                "binary": binary_path if 'has_fault' in df.columns else None,
                "multiclass": multiclass_path if 'fault_type' in df.columns else None,
                "summary": summary_path
            }
        except Exception as e:
            logger.error(f"Failed to process dataset variants: {str(e)}")
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
                "steel_quality_control": self._prepare_quality_control,
                "fault_detection": self._prepare_fault_detection,
                "fault_classification": self._prepare_fault_classification,
                "manufacturing_analytics": self._prepare_manufacturing_analytics,
                "predictive_maintenance": self._prepare_predictive_maintenance
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
        Prepare dataset for steel quality control offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the binary classification dataset
        binary_files = [f for f in os.listdir(self.binary_dir) if f.endswith('.csv')]
        if not binary_files:
            return {"success": False, "error": "No binary classification dataset found"}
        
        binary_path = os.path.join(self.binary_dir, binary_files[0])
        
        # Load the data
        df = pd.read_csv(binary_path)
        
        # Ensure we have the target column
        if "has_fault" not in df.columns:
            return {"success": False, "error": "Target column 'has_fault' not found"}
        
        # Prepare the dataset
        prepared_df = df.copy()
        
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
            "features": [col for col in prepared_df.columns if col != "has_fault"],
            "target": "has_fault",
            "samples": len(prepared_df),
            "positive_samples": int(prepared_df["has_fault"].sum()),
            "negative_samples": int((prepared_df["has_fault"] == 0).sum()),
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
        Prepare dataset for steel fault detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the binary classification dataset
        binary_files = [f for f in os.listdir(self.binary_dir) if f.endswith('.csv')]
        if not binary_files:
            return {"success": False, "error": "No binary classification dataset found"}
        
        binary_path = os.path.join(self.binary_dir, binary_files[0])
        
        # Load the data
        df = pd.read_csv(binary_path)
        
        # Ensure we have the target column
        if "has_fault" not in df.columns:
            return {"success": False, "error": "Target column 'has_fault' not found"}
        
        # Prepare the dataset
        prepared_df = df.copy()
        
        # Create a balanced dataset
        fault_samples = prepared_df[prepared_df["has_fault"] == 1]
        non_fault_samples = prepared_df[prepared_df["has_fault"] == 0].sample(
            n=min(len(fault_samples) * 2, (prepared_df["has_fault"] == 0).sum()),
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
            "features": [col for col in balanced_df.columns if col != "has_fault"],
            "target": "has_fault",
            "samples": len(balanced_df),
            "positive_samples": int(balanced_df["has_fault"].sum()),
            "negative_samples": int((balanced_df["has_fault"] == 0).sum()),
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
    
    def _prepare_fault_classification(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for steel fault classification offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the multiclass classification dataset
        multiclass_files = [f for f in os.listdir(self.multiclass_dir) if f.endswith('.csv')]
        if not multiclass_files:
            return {"success": False, "error": "No multiclass classification dataset found"}
        
        multiclass_path = os.path.join(self.multiclass_dir, multiclass_files[0])
        
        # Load the data
        df = pd.read_csv(multiclass_path)
        
        # Ensure we have the target columns
        if "fault_type" not in df.columns or "fault_type_encoded" not in df.columns:
            return {"success": False, "error": "Target columns not found"}
        
        # Prepare the dataset
        prepared_df = df.copy()
        
        # Filter out rows with no fault
        if "None" in prepared_df["fault_type"].unique():
            prepared_df = prepared_df[prepared_df["fault_type"] != "None"]
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Load fault type mapping
        mapping_path = os.path.join(self.metadata_dir, "fault_type_mapping.json")
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r') as f:
                fault_type_mapping = json.load(f)
        else:
            fault_type_mapping = {}
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "fault_classification",
            "features": [col for col in prepared_df.columns if col not in ["fault_type", "fault_type_encoded"]],
            "target": "fault_type_encoded",
            "target_readable": "fault_type",
            "samples": len(prepared_df),
            "class_distribution": prepared_df["fault_type"].value_counts().to_dict(),
            "class_mapping": fault_type_mapping,
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
        Prepare dataset for steel manufacturing analytics offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the processed dataset
        processed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('.csv') and f != "offers"]
        if not processed_files:
            return {"success": False, "error": "No processed dataset found"}
        
        processed_path = os.path.join(self.processed_dir, processed_files[0])
        
        # Load the data
        df = pd.read_csv(processed_path)
        
        # Prepare the dataset
        prepared_df = df.copy()
        
        # Get fault type columns
        fault_types = self.config.get("fault_types", [
            "Pastry", "Z_Scratch", "K_Scratch", "Stains", 
            "Dirtiness", "Bumps", "Other_Faults"
        ])
        
        # Filter to fault types that exist in the data
        fault_types = [ft for ft in fault_types if ft in df.columns]
        
        # Calculate feature importance using correlation with each fault type
        feature_cols = [col for col in df.columns if col not in fault_types and 
                       col not in ["fault_type", "fault_type_encoded", "has_fault"]]
        
        importance_dfs = []
        
        for fault in fault_types:
            if fault in df.columns:
                # Calculate correlation with this fault type
                correlations = df[feature_cols + [fault]].corr()[fault].drop(fault)
                
                # Create a dataframe with feature importance for this fault
                importance_df = pd.DataFrame({
                    "feature": correlations.index,
                    "importance": correlations.abs(),
                    "correlation": correlations,
                    "fault_type": fault
                }).sort_values("importance", ascending=False)
                
                importance_dfs.append(importance_df)
        
        # Combine all importance dataframes
        if importance_dfs:
            all_importance = pd.concat(importance_dfs)
            
            # Save feature importance
            importance_path = os.path.join(self.processed_dir, "offers", f"{offer_id}_feature_importance.csv")
            os.makedirs(os.path.dirname(importance_path), exist_ok=True)
            all_importance.to_csv(importance_path, index=False)
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "manufacturing_analytics",
            "features": feature_cols,
            "fault_types": fault_types,
            "samples": len(prepared_df),
            "fault_distribution": {ft: int(prepared_df[ft].sum()) for ft in fault_types if ft in prepared_df.columns},
            "file_paths": {
                "dataset": output_path,
                "feature_importance": importance_path if importance_dfs else None
            }
        }
        
        # Save metadata
        metadata_path = os.path.join(output_dir, f"{offer_id}_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "dataset_path": output_path,
            "importance_path": importance_path if importance_dfs else None,
            "metadata_path": metadata_path,
            "metadata": metadata
        }
    
    def _prepare_predictive_maintenance(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for steel predictive maintenance offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the binary classification dataset
        binary_files = [f for f in os.listdir(self.binary_dir) if f.endswith('.csv')]
        if not binary_files:
            return {"success": False, "error": "No binary classification dataset found"}
        
        binary_path = os.path.join(self.binary_dir, binary_files[0])
        
        # Load the data
        df = pd.read_csv(binary_path)
        
        # Ensure we have the target column
        if "has_fault" not in df.columns:
            return {"success": False, "error": "Target column 'has_fault' not found"}
        
        # Prepare the dataset
        prepared_df = df.copy()
        
        # Add a simulated time dimension for predictive maintenance
        # We'll create a sequence ID and a time step
        n_samples = len(prepared_df)
        n_sequences = 50  # Number of simulated production runs
        
        # Create sequence IDs
        sequence_ids = np.repeat(np.arange(1, n_sequences + 1), n_samples // n_sequences + 1)[:n_samples]
        prepared_df['sequence_id'] = sequence_ids
        
        # Create time steps within each sequence
        prepared_df['time_step'] = prepared_df.groupby('sequence_id').cumcount() + 1
        
        # Create a maintenance indicator
        # Maintenance is needed if a fault is detected
        prepared_df['maintenance_needed'] = prepared_df['has_fault']
        
        # Create a maintenance window
        # 0: No maintenance needed
        # 1: Maintenance needed soon (next 5 steps)
        # 2: Immediate maintenance needed
        prepared_df['maintenance_window'] = 0
        
        # For each sequence, if a fault is detected, set maintenance_window=2 for that step
        # and maintenance_window=1 for the 5 steps before it
        for seq_id in prepared_df['sequence_id'].unique():
            seq_mask = prepared_df['sequence_id'] == seq_id
            fault_steps = prepared_df.loc[seq_mask & (prepared_df['has_fault'] == 1), 'time_step'].values
            
            for fault_step in fault_steps:
                # Set immediate maintenance for the fault step
                prepared_df.loc[seq_mask & (prepared_df['time_step'] == fault_step), 'maintenance_window'] = 2
                
                # Set soon maintenance for the 5 steps before
                for i in range(1, 6):
                    if fault_step - i > 0:
                        prepared_df.loc[seq_mask & (prepared_df['time_step'] == fault_step - i), 'maintenance_window'] = 1
        
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
            "features": [col for col in prepared_df.columns if col not in ["has_fault", "maintenance_needed", "maintenance_window"]],
            "targets": ["maintenance_needed", "maintenance_window"],
            "samples": len(prepared_df),
            "sequences": int(prepared_df['sequence_id'].nunique()),
            "maintenance_distribution": {
                "no_maintenance": int((prepared_df['maintenance_window'] == 0).sum()),
                "soon_maintenance": int((prepared_df['maintenance_window'] == 1).sum()),
                "immediate_maintenance": int((prepared_df['maintenance_window'] == 2).sum())
            },
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
    
    # Create Steel Plates dataset connector
    connector = SteelPlatesDatasetConnector()
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        data_file="path/to/steel_plates_faults.data"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("steel_quality_control_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
