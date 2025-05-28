"""
Steel Energy Consumption Dataset Connector for Industriverse Data Layer

This module implements a protocol-native connector for the Steel Industry Energy Consumption
dataset, supporting MCP/A2A integration for industrial energy monitoring applications.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from .dataset_connector_base import DatasetConnectorBase

logger = logging.getLogger(__name__)

class SteelEnergyDatasetConnector(DatasetConnectorBase):
    """
    Connector for Steel Industry Energy Consumption Dataset.
    
    This connector provides protocol-native ingestion, validation, and
    transformation for the Steel Industry Energy Consumption dataset, with support
    for energy monitoring and optimization use cases.
    """
    
    def __init__(
        self,
        connector_id: str = "steel-energy-connector",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the Steel Energy dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "steel", "energy_optimization"],
            "intelligence_type": "energy_optimization",
            "feature_columns": [
                "date", "usage_kwh", "lagging_current_reactive_power", 
                "leading_current_reactive_power", "co2", "lagging_current_power_factor",
                "leading_current_power_factor", "nsm", "wday", "month", "year", "hour"
            ],
            "target_columns": ["usage_kwh"],
            "categorical_columns": ["wday", "month", "year", "hour"],
            "numerical_columns": [
                "lagging_current_reactive_power", "leading_current_reactive_power", 
                "co2", "lagging_current_power_factor", "leading_current_power_factor", "nsm"
            ],
            "datetime_columns": ["date"],
            "feature_descriptions": {
                "date": "Date and time of the measurement",
                "usage_kwh": "Energy consumption in kilowatt-hours",
                "lagging_current_reactive_power": "Lagging current reactive power in kVarh",
                "leading_current_reactive_power": "Leading current reactive power in kVarh",
                "co2": "CO2 emissions in ppm",
                "lagging_current_power_factor": "Lagging current power factor",
                "leading_current_power_factor": "Leading current power factor",
                "nsm": "Number of seconds from midnight",
                "wday": "Day of the week (1-7)",
                "month": "Month (1-12)",
                "year": "Year",
                "hour": "Hour of the day (0-23)"
            }
        }
        
        # Merge with provided config
        merged_config = default_config.copy()
        if config:
            merged_config.update(config)
        
        # Initialize base class
        super().__init__(
            connector_id=connector_id,
            dataset_name="steel_energy",
            dataset_type="timeseries",
            config=merged_config,
            secrets_manager=secrets_manager,
            manifest_path=manifest_path,
            base_dir=base_dir
        )
        
        # Set up dataset-specific directories
        self.processed_dir = os.path.join(self.base_dir, "processed")
        self.models_dir = os.path.join(self.processed_dir, "models")
        
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        logger.info("Initialized Steel Energy dataset connector")
    
    def ingest_dataset(
        self,
        data_path: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest the Steel Energy Consumption dataset.
        
        Args:
            data_path: Path to the dataset file
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
                        "data_path": data_path
                    }
                )
            
            # Ingest data
            result = self.ingest_data(
                source_path=data_path,
                validate=validate,
                transform=transform,
                emit_events=False
            )
            
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
        if source_path.endswith('.csv'):
            df = pd.read_csv(source_path)
        elif source_path.endswith('.xlsx') or source_path.endswith('.xls'):
            df = pd.read_excel(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        # Ensure column names match expected format
        # Convert to lowercase and replace spaces with underscores
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Ensure datetime column is properly parsed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        return df
    
    def _validate_data(self, data: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate the Steel Energy dataset.
        
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
        expected_columns = self.config["feature_columns"]
        missing_columns = [col for col in expected_columns if col not in data.columns]
        
        if missing_columns:
            errors.append(f"Missing expected columns: {missing_columns}")
        
        # Check for missing values
        missing_counts = data[expected_columns].isna().sum()
        columns_with_missing = missing_counts[missing_counts > 0]
        
        if not columns_with_missing.empty:
            warnings.append(f"Missing values found in columns: {columns_with_missing.to_dict()}")
        
        # Check for negative energy values
        if 'usage_kwh' in data.columns and (data['usage_kwh'] < 0).any():
            warnings.append("Negative energy consumption values found")
        
        # Check for out-of-range values in categorical columns
        for col in self.config["categorical_columns"]:
            if col in data.columns:
                if col == 'wday' and ((data[col] < 1) | (data[col] > 7)).any():
                    warnings.append(f"Out-of-range values found in {col} (should be 1-7)")
                elif col == 'month' and ((data[col] < 1) | (data[col] > 12)).any():
                    warnings.append(f"Out-of-range values found in {col} (should be 1-12)")
                elif col == 'hour' and ((data[col] < 0) | (data[col] > 23)).any():
                    warnings.append(f"Out-of-range values found in {col} (should be 0-23)")
        
        # Check for duplicate timestamps
        if 'date' in data.columns and data['date'].duplicated().any():
            warnings.append("Duplicate timestamps found")
        
        # Check for chronological order
        if 'date' in data.columns and not data['date'].equals(data['date'].sort_values()):
            warnings.append("Data is not in chronological order")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _transform_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the Steel Energy dataset.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Handle missing values
        for col in self.config["numerical_columns"]:
            if col in df.columns and df[col].isna().any():
                # Fill missing values with median
                df[col] = df[col].fillna(df[col].median())
        
        # Ensure datetime column is properly parsed
        if 'date' in df.columns and not pd.api.types.is_datetime64_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        # Extract additional datetime features if not already present
        if 'date' in df.columns:
            if 'wday' not in df.columns:
                df['wday'] = df['date'].dt.dayofweek + 1  # 1-7
            
            if 'month' not in df.columns:
                df['month'] = df['date'].dt.month
            
            if 'year' not in df.columns:
                df['year'] = df['date'].dt.year
            
            if 'hour' not in df.columns:
                df['hour'] = df['date'].dt.hour
            
            if 'nsm' not in df.columns:
                # Number of seconds from midnight
                df['nsm'] = df['date'].dt.hour * 3600 + df['date'].dt.minute * 60 + df['date'].dt.second
        
        # Normalize numerical features
        scaler = StandardScaler()
        numerical_cols = [col for col in self.config["numerical_columns"] if col in df.columns]
        
        if numerical_cols:
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            
            # Save the scaler for later use
            import pickle
            scaler_path = os.path.join(self.models_dir, "numerical_scaler.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
        
        # Normalize target variable separately
        if 'usage_kwh' in df.columns:
            target_scaler = MinMaxScaler()
            df['usage_kwh_normalized'] = target_scaler.fit_transform(df[['usage_kwh']])
            
            # Save the target scaler
            import pickle
            target_scaler_path = os.path.join(self.models_dir, "target_scaler.pkl")
            with open(target_scaler_path, 'wb') as f:
                pickle.dump(target_scaler, f)
        
        # Create cyclical features for time variables
        if 'hour' in df.columns:
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        if 'wday' in df.columns:
            df['wday_sin'] = np.sin(2 * np.pi * df['wday'] / 7)
            df['wday_cos'] = np.cos(2 * np.pi * df['wday'] / 7)
        
        if 'month' in df.columns:
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Create energy consumption categories
        if 'usage_kwh' in df.columns:
            # Define consumption categories based on quantiles
            low_threshold = df['usage_kwh'].quantile(0.33)
            high_threshold = df['usage_kwh'].quantile(0.67)
            
            df['consumption_category'] = pd.cut(
                df['usage_kwh'],
                bins=[float('-inf'), low_threshold, high_threshold, float('inf')],
                labels=['low', 'medium', 'high']
            )
        
        # Create lagging features (previous values)
        if 'usage_kwh' in df.columns:
            for lag in [1, 2, 3, 6, 12, 24]:  # Different time lags
                df[f'usage_kwh_lag_{lag}'] = df['usage_kwh'].shift(lag)
        
        # Create rolling statistics
        if 'usage_kwh' in df.columns:
            for window in [3, 6, 12, 24]:  # Different window sizes
                df[f'usage_kwh_rolling_mean_{window}'] = df['usage_kwh'].rolling(window=window, min_periods=1).mean()
                df[f'usage_kwh_rolling_std_{window}'] = df['usage_kwh'].rolling(window=window, min_periods=1).std()
        
        # Fill any new missing values created by lagging/rolling operations
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        # Calculate correlations with target
        if 'usage_kwh' in df.columns:
            numerical_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col != 'usage_kwh']
            correlations = df[numerical_cols + ['usage_kwh']].corr()['usage_kwh'].sort_values(ascending=False)
            
            # Save correlations
            corr_path = os.path.join(self.metadata_dir, "target_correlations.csv")
            correlations.to_csv(corr_path)
        
        return df
    
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
                "energy_consumption_prediction": self._prepare_energy_prediction,
                "energy_optimization": self._prepare_energy_optimization,
                "anomaly_detection": self._prepare_anomaly_detection,
                "consumption_classification": self._prepare_consumption_classification,
                "co2_reduction": self._prepare_co2_reduction
            }
            
            # Find the appropriate preparation method
            preparation_method = None
            for offer_prefix, method in offer_mappings.items():
                if offer_id.startswith(offer_prefix):
                    preparation_method = method
                    break
            
            # Use default method if no specific method found
            if preparation_method is None:
                preparation_method = self._prepare_energy_prediction
            
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
    
    def _prepare_energy_prediction(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for energy consumption prediction offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.processed_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Ensure date column is properly parsed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Get feature columns for prediction
        feature_cols = [
            'lagging_current_reactive_power', 'leading_current_reactive_power', 
            'co2', 'lagging_current_power_factor', 'leading_current_power_factor', 
            'nsm', 'hour_sin', 'hour_cos', 'wday_sin', 'wday_cos', 'month_sin', 'month_cos'
        ]
        
        # Add lagging features
        lag_cols = [col for col in df.columns if col.startswith('usage_kwh_lag_')]
        feature_cols.extend(lag_cols)
        
        # Add rolling statistics
        rolling_cols = [col for col in df.columns if col.startswith('usage_kwh_rolling_')]
        feature_cols.extend(rolling_cols)
        
        # Filter to only include columns that exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Prepare the dataset
        prepared_df = df[['date'] + feature_cols + ['usage_kwh', 'usage_kwh_normalized']].copy()
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "energy_prediction",
            "features": feature_cols,
            "target": "usage_kwh",
            "target_normalized": "usage_kwh_normalized",
            "samples": len(prepared_df),
            "time_range": {
                "start": prepared_df['date'].min().strftime('%Y-%m-%d %H:%M:%S'),
                "end": prepared_df['date'].max().strftime('%Y-%m-%d %H:%M:%S')
            },
            "statistics": {
                "mean_usage": float(prepared_df['usage_kwh'].mean()),
                "std_usage": float(prepared_df['usage_kwh'].std()),
                "min_usage": float(prepared_df['usage_kwh'].min()),
                "max_usage": float(prepared_df['usage_kwh'].max())
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
    
    def _prepare_energy_optimization(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for energy optimization offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.processed_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Ensure date column is properly parsed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Get all relevant columns
        feature_cols = [
            'lagging_current_reactive_power', 'leading_current_reactive_power', 
            'co2', 'lagging_current_power_factor', 'leading_current_power_factor', 
            'nsm', 'hour', 'wday', 'month', 'year'
        ]
        
        # Filter to only include columns that exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Prepare the dataset
        prepared_df = df[['date'] + feature_cols + ['usage_kwh']].copy()
        
        # Add time-based aggregations
        if 'date' in prepared_df.columns:
            # Add hour of day aggregation
            hourly_avg = prepared_df.groupby('hour')['usage_kwh'].mean().reset_index()
            hourly_avg.columns = ['hour', 'avg_usage_by_hour']
            prepared_df = pd.merge(prepared_df, hourly_avg, on='hour', how='left')
            
            # Add day of week aggregation
            daily_avg = prepared_df.groupby('wday')['usage_kwh'].mean().reset_index()
            daily_avg.columns = ['wday', 'avg_usage_by_wday']
            prepared_df = pd.merge(prepared_df, daily_avg, on='wday', how='left')
            
            # Add month aggregation
            monthly_avg = prepared_df.groupby('month')['usage_kwh'].mean().reset_index()
            monthly_avg.columns = ['month', 'avg_usage_by_month']
            prepared_df = pd.merge(prepared_df, monthly_avg, on='month', how='left')
        
        # Calculate optimization potential
        if 'avg_usage_by_hour' in prepared_df.columns:
            prepared_df['optimization_potential'] = prepared_df['usage_kwh'] - prepared_df['avg_usage_by_hour']
            prepared_df['optimization_potential_pct'] = (prepared_df['optimization_potential'] / prepared_df['usage_kwh']) * 100
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "energy_optimization",
            "features": feature_cols,
            "target": "usage_kwh",
            "samples": len(prepared_df),
            "time_range": {
                "start": prepared_df['date'].min().strftime('%Y-%m-%d %H:%M:%S'),
                "end": prepared_df['date'].max().strftime('%Y-%m-%d %H:%M:%S')
            },
            "optimization_metrics": {
                "avg_optimization_potential": float(prepared_df['optimization_potential'].mean()),
                "max_optimization_potential": float(prepared_df['optimization_potential'].max()),
                "avg_optimization_potential_pct": float(prepared_df['optimization_potential_pct'].mean())
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
    
    def _prepare_anomaly_detection(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for energy consumption anomaly detection offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.processed_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Ensure date column is properly parsed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Get feature columns
        feature_cols = [
            'lagging_current_reactive_power', 'leading_current_reactive_power', 
            'co2', 'lagging_current_power_factor', 'leading_current_power_factor', 
            'nsm', 'hour_sin', 'hour_cos', 'wday_sin', 'wday_cos', 'month_sin', 'month_cos'
        ]
        
        # Add rolling statistics
        rolling_cols = [col for col in df.columns if col.startswith('usage_kwh_rolling_')]
        feature_cols.extend(rolling_cols)
        
        # Filter to only include columns that exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Create anomaly indicator
        if 'usage_kwh' in df.columns and 'usage_kwh_rolling_mean_24' in df.columns:
            # Calculate z-score
            df['usage_kwh_zscore'] = np.abs((df['usage_kwh'] - df['usage_kwh_rolling_mean_24']) / df['usage_kwh_rolling_std_24'].replace(0, 1))
            
            # Define anomalies as points with z-score > 3
            df['anomaly'] = (df['usage_kwh_zscore'] > 3).astype(int)
        else:
            # Create a dummy anomaly column (10% anomalies)
            np.random.seed(42)
            df['anomaly'] = (np.random.rand(len(df)) < 0.1).astype(int)
        
        # Prepare the dataset
        prepared_df = df[['date'] + feature_cols + ['usage_kwh', 'anomaly']].copy()
        
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
            "features": feature_cols,
            "target": "anomaly",
            "samples": len(balanced_df),
            "normal_samples": int((balanced_df["anomaly"] == 0).sum()),
            "anomaly_samples": int(balanced_df["anomaly"].sum()),
            "time_range": {
                "start": balanced_df['date'].min().strftime('%Y-%m-%d %H:%M:%S'),
                "end": balanced_df['date'].max().strftime('%Y-%m-%d %H:%M:%S')
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
    
    def _prepare_consumption_classification(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for energy consumption classification offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.processed_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Ensure date column is properly parsed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Get feature columns
        feature_cols = [
            'lagging_current_reactive_power', 'leading_current_reactive_power', 
            'co2', 'lagging_current_power_factor', 'leading_current_power_factor', 
            'nsm', 'hour_sin', 'hour_cos', 'wday_sin', 'wday_cos', 'month_sin', 'month_cos'
        ]
        
        # Filter to only include columns that exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Ensure consumption category exists
        if 'consumption_category' not in df.columns and 'usage_kwh' in df.columns:
            # Define consumption categories based on quantiles
            low_threshold = df['usage_kwh'].quantile(0.33)
            high_threshold = df['usage_kwh'].quantile(0.67)
            
            df['consumption_category'] = pd.cut(
                df['usage_kwh'],
                bins=[float('-inf'), low_threshold, high_threshold, float('inf')],
                labels=['low', 'medium', 'high']
            )
        
        # Prepare the dataset
        prepared_df = df[['date'] + feature_cols + ['usage_kwh', 'consumption_category']].copy()
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "consumption_classification",
            "features": feature_cols,
            "target": "consumption_category",
            "samples": len(prepared_df),
            "class_distribution": prepared_df["consumption_category"].value_counts().to_dict(),
            "time_range": {
                "start": prepared_df['date'].min().strftime('%Y-%m-%d %H:%M:%S'),
                "end": prepared_df['date'].max().strftime('%Y-%m-%d %H:%M:%S')
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
    
    def _prepare_co2_reduction(self, offer_id: str) -> Dict[str, Any]:
        """
        Prepare dataset for CO2 reduction offer.
        
        Args:
            offer_id: ID of the offer
            
        Returns:
            Dictionary with prepared dataset information
        """
        # Find the transformed dataset
        transformed_files = [f for f in os.listdir(self.processed_dir) if f.endswith('_transformed.csv')]
        if not transformed_files:
            return {"success": False, "error": "No transformed dataset found"}
        
        transformed_path = os.path.join(self.processed_dir, transformed_files[0])
        
        # Load the data
        df = pd.read_csv(transformed_path)
        
        # Ensure date column is properly parsed
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Check if CO2 column exists
        if 'co2' not in df.columns:
            return {"success": False, "error": "CO2 column not found in dataset"}
        
        # Get feature columns
        feature_cols = [
            'lagging_current_reactive_power', 'leading_current_reactive_power', 
            'lagging_current_power_factor', 'leading_current_power_factor', 
            'nsm', 'hour', 'wday', 'month', 'year', 'usage_kwh'
        ]
        
        # Filter to only include columns that exist in the dataframe
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Prepare the dataset
        prepared_df = df[['date'] + feature_cols + ['co2']].copy()
        
        # Calculate CO2 per kWh
        if 'usage_kwh' in prepared_df.columns:
            prepared_df['co2_per_kwh'] = prepared_df['co2'] / prepared_df['usage_kwh'].replace(0, np.nan)
            prepared_df['co2_per_kwh'] = prepared_df['co2_per_kwh'].fillna(prepared_df['co2_per_kwh'].median())
        
        # Add time-based aggregations
        if 'date' in prepared_df.columns:
            # Add hour of day aggregation
            hourly_avg = prepared_df.groupby('hour')['co2'].mean().reset_index()
            hourly_avg.columns = ['hour', 'avg_co2_by_hour']
            prepared_df = pd.merge(prepared_df, hourly_avg, on='hour', how='left')
            
            # Add day of week aggregation
            daily_avg = prepared_df.groupby('wday')['co2'].mean().reset_index()
            daily_avg.columns = ['wday', 'avg_co2_by_wday']
            prepared_df = pd.merge(prepared_df, daily_avg, on='wday', how='left')
        
        # Calculate reduction potential
        if 'avg_co2_by_hour' in prepared_df.columns:
            prepared_df['co2_reduction_potential'] = prepared_df['co2'] - prepared_df['avg_co2_by_hour']
            prepared_df['co2_reduction_potential_pct'] = (prepared_df['co2_reduction_potential'] / prepared_df['co2']) * 100
        
        # Save prepared dataset
        output_dir = os.path.join(self.processed_dir, "offers")
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f"{offer_id}_dataset.csv")
        prepared_df.to_csv(output_path, index=False)
        
        # Create metadata
        metadata = {
            "offer_id": offer_id,
            "dataset_name": self.dataset_name,
            "preparation_method": "co2_reduction",
            "features": feature_cols,
            "target": "co2",
            "samples": len(prepared_df),
            "time_range": {
                "start": prepared_df['date'].min().strftime('%Y-%m-%d %H:%M:%S'),
                "end": prepared_df['date'].max().strftime('%Y-%m-%d %H:%M:%S')
            },
            "co2_metrics": {
                "avg_co2": float(prepared_df['co2'].mean()),
                "max_co2": float(prepared_df['co2'].max()),
                "min_co2": float(prepared_df['co2'].min())
            }
        }
        
        if 'co2_reduction_potential' in prepared_df.columns:
            metadata["reduction_metrics"] = {
                "avg_reduction_potential": float(prepared_df['co2_reduction_potential'].mean()),
                "max_reduction_potential": float(prepared_df['co2_reduction_potential'].max()),
                "avg_reduction_potential_pct": float(prepared_df['co2_reduction_potential_pct'].mean())
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
    
    # Create Steel Energy dataset connector
    connector = SteelEnergyDatasetConnector()
    
    # Initialize connector
    connector.initialize()
    
    # Ingest dataset
    result = connector.ingest_dataset(
        data_path="path/to/steel_energy_data.csv"
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
    
    # Prepare dataset for an offer
    offer_result = connector.get_dataset_for_offer("energy_consumption_prediction_001")
    print(f"Offer dataset preparation: {json.dumps(offer_result, indent=2)}")
