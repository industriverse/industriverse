"""
Data Processing Engine for Industriverse Data Layer

This module implements a protocol-native data processing engine that handles
transformation, feature engineering, and preparation of industrial datasets
for analysis and model training.
"""

import json
import logging
import os
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Union, Callable
from datetime import datetime
import pickle
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

class DataProcessingEngine:
    """
    Protocol-native data processing engine for industrial datasets.
    
    This engine provides data transformation, feature engineering, and preparation
    capabilities for industrial datasets, with full MCP/A2A protocol integration.
    """
    
    def __init__(
        self,
        engine_id: str = "data-processing-engine",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the data processing engine.
        
        Args:
            engine_id: Unique identifier for this engine
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for engine files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "process_industry", "energy"],
            "intelligence_type": "data_transformation",
            "processing_modes": ["batch", "streaming"],
            "default_mode": "batch",
            "max_batch_size": 10000,
            "feature_engineering": {
                "enable_auto_feature_engineering": True,
                "max_lag_features": 24,
                "enable_cyclical_features": True,
                "enable_interaction_features": True,
                "max_polynomial_degree": 2
            },
            "preprocessing": {
                "scaling_method": "standard",  # standard, minmax, robust
                "imputation_method": "knn",    # mean, median, knn, constant
                "outlier_detection": "iqr",    # iqr, zscore, isolation_forest
                "outlier_treatment": "clip"    # clip, remove, impute
            },
            "feature_selection": {
                "enable_auto_selection": True,
                "method": "mutual_info",       # mutual_info, f_regression, pca
                "max_features": 50,
                "variance_threshold": 0.01
            }
        }
        
        # Merge with provided config
        self.config = default_config.copy()
        if config:
            self.config.update(config)
        
        self.engine_id = engine_id
        self.secrets_manager = secrets_manager
        
        # Set up base directory
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.join(os.getcwd(), "data_processing")
        
        # Set up subdirectories
        self.processed_dir = os.path.join(self.base_dir, "processed")
        self.models_dir = os.path.join(self.base_dir, "models")
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.temp_dir = os.path.join(self.base_dir, "temp")
        
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Set up agent manifest
        self.manifest_path = manifest_path
        if not self.manifest_path:
            self.manifest_path = os.path.join(self.base_dir, "agent_manifest.yaml")
        
        # Initialize protocol integration
        self._initialize_protocol_integration()
        
        # Initialize processing pipelines
        self._initialize_processing_pipelines()
        
        logger.info(f"Initialized data processing engine: {self.engine_id}")
    
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
                agent_id=self.engine_id,
                agent_type="data_processing_engine",
                manifest_path=self.manifest_path,
                intelligence_type=self.config["intelligence_type"],
                industry_tags=self.config["industry_tags"]
            )
            
            # Initialize protocol translator
            self.protocol_translator = ProtocolTranslator(
                agent_id=self.engine_id,
                supported_protocols=["mcp", "a2a"]
            )
            
            # Initialize mesh boot lifecycle
            self.mesh_lifecycle = MeshBootLifecycle(
                agent_id=self.engine_id,
                agent_core=self.agent_core
            )
            
            # Register with mesh
            self.mesh_lifecycle.register()
            
            # Initialize event handlers
            self._initialize_event_handlers()
            
            logger.info(f"Protocol integration initialized for {self.engine_id}")
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
            if "dataset_ingestion_completed" in event.get("status", ""):
                # New dataset ingested, process it
                dataset_name = event.get("dataset", "")
                if dataset_name:
                    logger.info(f"Observed new dataset ingestion: {dataset_name}")
                    # Schedule processing
                    return {
                        "status": "processing_scheduled",
                        "dataset": dataset_name,
                        "engine_id": self.engine_id
                    }
            
            return {"status": "observed", "engine_id": self.engine_id}
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
            if "processing_pipeline" in event:
                # Simulate processing pipeline
                pipeline_config = event.get("processing_pipeline", {})
                dataset_name = event.get("dataset", "")
                
                if dataset_name:
                    logger.info(f"Simulating processing pipeline for {dataset_name}")
                    # Return simulated metrics
                    return {
                        "status": "simulation_completed",
                        "dataset": dataset_name,
                        "engine_id": self.engine_id,
                        "simulated_metrics": {
                            "processing_time": 120.5,
                            "memory_usage": "2.3 GB",
                            "output_rows": 10000,
                            "output_columns": 50
                        }
                    }
            
            return {"status": "simulated", "engine_id": self.engine_id}
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
                # Recommend processing pipeline
                dataset_name = event.get("dataset", "")
                
                if dataset_name:
                    logger.info(f"Recommending processing pipeline for {dataset_name}")
                    # Return recommended pipeline
                    return {
                        "status": "recommendation_provided",
                        "dataset": dataset_name,
                        "engine_id": self.engine_id,
                        "recommended_pipeline": {
                            "preprocessing": {
                                "scaling_method": "standard",
                                "imputation_method": "knn",
                                "outlier_detection": "iqr"
                            },
                            "feature_engineering": {
                                "lag_features": [1, 6, 12, 24],
                                "cyclical_features": ["hour", "day", "month"],
                                "interaction_features": True
                            },
                            "feature_selection": {
                                "method": "mutual_info",
                                "max_features": 30
                            }
                        }
                    }
            
            return {"status": "recommendation_provided", "engine_id": self.engine_id}
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
            if "process_dataset" in event.get("action", ""):
                # Process dataset
                dataset_name = event.get("dataset", "")
                dataset_path = event.get("dataset_path", "")
                pipeline_config = event.get("pipeline_config", {})
                
                if dataset_path and os.path.exists(dataset_path):
                    logger.info(f"Processing dataset: {dataset_name}")
                    # Process dataset
                    result = self.process_dataset(
                        dataset_path=dataset_path,
                        dataset_name=dataset_name,
                        config=pipeline_config
                    )
                    
                    return {
                        "status": "processing_completed" if result["success"] else "processing_failed",
                        "dataset": dataset_name,
                        "engine_id": self.engine_id,
                        "result": result
                    }
            
            return {"status": "action_completed", "engine_id": self.engine_id}
        except Exception as e:
            logger.error(f"Error handling act event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_processing_pipelines(self):
        """Initialize data processing pipelines."""
        # Initialize preprocessing pipelines
        self.preprocessing_pipelines = {
            "standard": Pipeline([
                ('imputer', self._get_imputer()),
                ('scaler', StandardScaler())
            ]),
            "minmax": Pipeline([
                ('imputer', self._get_imputer()),
                ('scaler', MinMaxScaler())
            ]),
            "robust": Pipeline([
                ('imputer', self._get_imputer()),
                ('scaler', RobustScaler())
            ])
        }
        
        # Initialize feature selection pipelines
        self.feature_selection_pipelines = {
            "mutual_info": SelectKBest(mutual_info_regression),
            "f_regression": SelectKBest(f_regression),
            "pca": PCA()
        }
        
        logger.info("Processing pipelines initialized")
    
    def _get_imputer(self) -> SimpleImputer:
        """
        Get imputer based on configuration.
        
        Returns:
            Configured imputer
        """
        imputation_method = self.config["preprocessing"]["imputation_method"]
        
        if imputation_method == "mean":
            return SimpleImputer(strategy="mean")
        elif imputation_method == "median":
            return SimpleImputer(strategy="median")
        elif imputation_method == "constant":
            return SimpleImputer(strategy="constant", fill_value=0)
        elif imputation_method == "knn":
            return KNNImputer(n_neighbors=5)
        else:
            # Default to KNN
            return KNNImputer(n_neighbors=5)
    
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
            # Add engine ID to payload
            payload["engine_id"] = self.engine_id
            
            # Add timestamp
            payload["timestamp"] = datetime.now().isoformat()
            
            # Emit event
            self.agent_core.emit_event(event_type, payload)
            return True
        except Exception as e:
            logger.error(f"Failed to emit event: {str(e)}")
            return False
    
    def process_dataset(
        self,
        dataset_path: str,
        dataset_name: str = "",
        config: Optional[Dict[str, Any]] = None,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Process a dataset.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            config: Processing configuration
            emit_events: Whether to emit protocol events
            
        Returns:
            Processing result
        """
        try:
            # Start processing
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_processing_started",
                        "dataset": dataset_name,
                        "dataset_path": dataset_path
                    }
                )
            
            # Determine dataset type
            dataset_type = self._determine_dataset_type(dataset_path)
            
            # Load dataset
            data = self._load_dataset(dataset_path, dataset_type)
            
            # Merge configuration
            processing_config = self.config.copy()
            if config:
                # Update nested dictionaries
                for key, value in config.items():
                    if isinstance(value, dict) and key in processing_config and isinstance(processing_config[key], dict):
                        processing_config[key].update(value)
                    else:
                        processing_config[key] = value
            
            # Process dataset based on type
            if dataset_type == "timeseries":
                result = self._process_timeseries_dataset(data, dataset_name, processing_config)
            elif dataset_type == "tabular":
                result = self._process_tabular_dataset(data, dataset_name, processing_config)
            elif dataset_type == "image":
                result = self._process_image_dataset(data, dataset_name, processing_config)
            else:
                result = self._process_generic_dataset(data, dataset_name, processing_config)
            
            # Complete processing
            end_time = time.time()
            duration = end_time - start_time
            
            # Add processing metadata
            result["processing_time"] = duration
            result["processed_at"] = datetime.now().isoformat()
            result["engine_id"] = self.engine_id
            result["config"] = processing_config
            
            # Save processing metadata
            metadata_path = os.path.join(self.metadata_dir, f"{dataset_name}_processing_metadata.json")
            with open(metadata_path, 'w') as f:
                # Convert non-serializable objects to strings
                serializable_result = self._make_serializable(result)
                json.dump(serializable_result, f, indent=2)
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_processing_completed",
                        "dataset": dataset_name,
                        "processing_time": duration,
                        "output_path": result.get("output_path", ""),
                        "statistics": result.get("statistics", {})
                    }
                )
            
            logger.info(f"Completed dataset processing for {dataset_name} in {duration:.2f}s")
            return {
                "success": True,
                "dataset": dataset_name,
                "output_path": result.get("output_path", ""),
                "metadata_path": metadata_path,
                "processing_time": duration,
                "statistics": result.get("statistics", {})
            }
        except Exception as e:
            logger.error(f"Failed to process dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_processing_failed",
                        "dataset": dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "dataset": dataset_name,
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def _make_serializable(self, obj: Any) -> Any:
        """
        Make an object JSON serializable.
        
        Args:
            obj: Object to make serializable
            
        Returns:
            Serializable object
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return "DataFrame: " + str(obj.shape)
        elif isinstance(obj, pd.Series):
            return "Series: " + str(obj.shape)
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj
    
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
        else:
            return "unknown"
    
    def _load_dataset(self, dataset_path: str, dataset_type: str) -> Any:
        """
        Load dataset from file.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_type: Type of dataset
            
        Returns:
            Loaded dataset
        """
        if dataset_type in ["timeseries", "tabular"]:
            if dataset_path.endswith('.csv'):
                return pd.read_csv(dataset_path)
            elif dataset_path.endswith(('.xlsx', '.xls')):
                return pd.read_excel(dataset_path)
        elif dataset_type == "image":
            if dataset_path.endswith('.json'):
                with open(dataset_path, 'r') as f:
                    return json.load(f)
            else:
                # Single image file
                return {"image_path": dataset_path}
        elif dataset_type == "json":
            with open(dataset_path, 'r') as f:
                return json.load(f)
        else:
            # Generic file loading
            with open(dataset_path, 'rb') as f:
                return f.read()
    
    def _process_timeseries_dataset(
        self,
        data: pd.DataFrame,
        dataset_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a time series dataset.
        
        Args:
            data: Dataset to process
            dataset_name: Name of the dataset
            config: Processing configuration
            
        Returns:
            Processing result
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Identify datetime columns
        datetime_cols = []
        for col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col])
                datetime_cols.append(col)
            except:
                pass
        
        if not datetime_cols:
            logger.warning(f"No datetime columns found in {dataset_name}")
            # Treat as tabular dataset
            return self._process_tabular_dataset(data, dataset_name, config)
        
        # Use the first datetime column as the index
        date_col = datetime_cols[0]
        df.set_index(date_col, inplace=True)
        
        # Sort by datetime index
        df.sort_index(inplace=True)
        
        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Handle missing values
        if numeric_cols:
            imputer = self._get_imputer()
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        # Handle categorical columns
        for col in categorical_cols:
            df[col] = df[col].fillna('unknown')
            # One-hot encode if needed
            if len(df[col].unique()) < 10:  # Only encode if few unique values
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
        
        # Feature engineering for time series
        if config["feature_engineering"]["enable_auto_feature_engineering"]:
            df = self._engineer_timeseries_features(df, config)
        
        # Scale numeric features
        scaling_method = config["preprocessing"]["scaling_method"]
        if scaling_method in self.preprocessing_pipelines and numeric_cols:
            # Get updated numeric columns after feature engineering
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            # Fit and transform
            scaler = self.preprocessing_pipelines[scaling_method].named_steps['scaler']
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            
            # Save the scaler
            scaler_path = os.path.join(self.models_dir, f"{dataset_name}_scaler.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
        
        # Feature selection if enabled
        if config["feature_selection"]["enable_auto_selection"]:
            df = self._perform_feature_selection(df, config)
        
        # Save processed dataset
        output_path = os.path.join(self.processed_dir, f"{dataset_name}_processed.csv")
        df.to_csv(output_path)
        
        # Calculate statistics
        statistics = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_columns": len(df.select_dtypes(include=['number']).columns),
            "categorical_columns": len(df.select_dtypes(include=['object', 'category']).columns),
            "datetime_columns": len(datetime_cols),
            "missing_values": df.isna().sum().sum(),
            "time_range": {
                "start": df.index.min().strftime('%Y-%m-%d %H:%M:%S') if not df.empty else None,
                "end": df.index.max().strftime('%Y-%m-%d %H:%M:%S') if not df.empty else None
            }
        }
        
        return {
            "output_path": output_path,
            "statistics": statistics,
            "feature_columns": df.columns.tolist(),
            "datetime_columns": datetime_cols,
            "dataset_type": "timeseries"
        }
    
    def _engineer_timeseries_features(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Engineer features for time series data.
        
        Args:
            df: DataFrame with time series data
            config: Processing configuration
            
        Returns:
            DataFrame with engineered features
        """
        # Extract datetime components
        df['hour'] = df.index.hour
        df['day'] = df.index.day
        df['dayofweek'] = df.index.dayofweek
        df['month'] = df.index.month
        df['quarter'] = df.index.quarter
        df['year'] = df.index.year
        
        # Create cyclical features for datetime components
        if config["feature_engineering"]["enable_cyclical_features"]:
            # Hour of day
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            
            # Day of week
            df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
            df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
            
            # Month
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Create lag features
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Exclude datetime component columns
        exclude_cols = ['hour', 'day', 'dayofweek', 'month', 'quarter', 'year', 
                        'hour_sin', 'hour_cos', 'dayofweek_sin', 'dayofweek_cos', 
                        'month_sin', 'month_cos']
        
        target_cols = [col for col in numeric_cols if col not in exclude_cols]
        
        # Create lag features for selected columns
        max_lag = min(config["feature_engineering"]["max_lag_features"], len(df) // 10)
        
        for col in target_cols[:5]:  # Limit to first 5 numeric columns to avoid explosion
            for lag in [1, 6, 12, 24, 48, 168]:  # Common lags (hour, 6h, 12h, day, 2d, week)
                if lag <= max_lag:
                    df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        # Create rolling window features
        for col in target_cols[:5]:
            for window in [6, 12, 24, 48, 168]:  # Common windows
                if window <= max_lag:
                    df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window, min_periods=1).mean()
                    df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window, min_periods=1).std()
        
        # Create interaction features
        if config["feature_engineering"]["enable_interaction_features"]:
            # Limit to first 3 numeric columns to avoid explosion
            for i, col1 in enumerate(target_cols[:3]):
                for col2 in target_cols[i+1:4]:  # Limit to next 3 columns
                    df[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
        
        # Fill NaN values created by lag/rolling features
        df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
        
        return df
    
    def _process_tabular_dataset(
        self,
        data: pd.DataFrame,
        dataset_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a tabular dataset.
        
        Args:
            data: Dataset to process
            dataset_name: Name of the dataset
            config: Processing configuration
            
        Returns:
            Processing result
        """
        # Create a copy to avoid modifying the original
        df = data.copy()
        
        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Handle missing values
        if numeric_cols:
            imputer = self._get_imputer()
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        # Handle categorical columns
        for col in categorical_cols:
            df[col] = df[col].fillna('unknown')
            # One-hot encode if needed
            if len(df[col].unique()) < 10:  # Only encode if few unique values
                dummies = pd.get_dummies(df[col], prefix=col)
                df = pd.concat([df.drop(col, axis=1), dummies], axis=1)
        
        # Feature engineering for tabular data
        if config["feature_engineering"]["enable_auto_feature_engineering"]:
            df = self._engineer_tabular_features(df, config)
        
        # Scale numeric features
        scaling_method = config["preprocessing"]["scaling_method"]
        if scaling_method in self.preprocessing_pipelines and numeric_cols:
            # Get updated numeric columns after feature engineering
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            # Fit and transform
            scaler = self.preprocessing_pipelines[scaling_method].named_steps['scaler']
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            
            # Save the scaler
            scaler_path = os.path.join(self.models_dir, f"{dataset_name}_scaler.pkl")
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
        
        # Feature selection if enabled
        if config["feature_selection"]["enable_auto_selection"]:
            df = self._perform_feature_selection(df, config)
        
        # Save processed dataset
        output_path = os.path.join(self.processed_dir, f"{dataset_name}_processed.csv")
        df.to_csv(output_path, index=False)
        
        # Calculate statistics
        statistics = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "numeric_columns": len(df.select_dtypes(include=['number']).columns),
            "categorical_columns": len(df.select_dtypes(include=['object', 'category']).columns),
            "missing_values": df.isna().sum().sum()
        }
        
        return {
            "output_path": output_path,
            "statistics": statistics,
            "feature_columns": df.columns.tolist(),
            "dataset_type": "tabular"
        }
    
    def _engineer_tabular_features(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Engineer features for tabular data.
        
        Args:
            df: DataFrame with tabular data
            config: Processing configuration
            
        Returns:
            DataFrame with engineered features
        """
        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # Create polynomial features
        if config["feature_engineering"]["enable_interaction_features"]:
            # Limit to first 5 numeric columns to avoid explosion
            target_cols = numeric_cols[:5]
            
            # Create interaction features
            for i, col1 in enumerate(target_cols):
                for col2 in target_cols[i+1:]:
                    df[f'{col1}_{col2}_interaction'] = df[col1] * df[col2]
            
            # Create polynomial features if configured
            max_degree = config["feature_engineering"]["max_polynomial_degree"]
            if max_degree >= 2:
                for col in target_cols:
                    for degree in range(2, max_degree + 1):
                        df[f'{col}_power_{degree}'] = df[col] ** degree
        
        # Create binned features for numeric columns
        for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
            # Create 5 bins
            df[f'{col}_binned'] = pd.qcut(df[col], q=5, labels=False, duplicates='drop')
        
        # Create ratio features
        for i, col1 in enumerate(numeric_cols[:3]):  # Limit to first 3 numeric columns
            for col2 in numeric_cols[i+1:4]:  # Limit to next 3 columns
                # Avoid division by zero
                denominator = df[col2].replace(0, np.nan)
                df[f'{col1}_to_{col2}_ratio'] = df[col1] / denominator
        
        # Fill NaN values created by feature engineering
        df = df.fillna(0)
        
        return df
    
    def _process_image_dataset(
        self,
        data: Any,
        dataset_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an image dataset.
        
        Args:
            data: Dataset to process
            dataset_name: Name of the dataset
            config: Processing configuration
            
        Returns:
            Processing result
        """
        # For image datasets, we primarily organize metadata
        if isinstance(data, dict) and "image_path" in data:
            # Single image
            images = [data]
        elif isinstance(data, list) and len(data) > 0 and "image_path" in data[0]:
            # List of images
            images = data
        else:
            raise ValueError(f"Unsupported image dataset format for {dataset_name}")
        
        # Create dataset index
        dataset_index = []
        
        for i, item in enumerate(images):
            index_item = {
                "id": i,
                "image_path": item["image_path"],
                "file_name": os.path.basename(item["image_path"])
            }
            
            # Copy other metadata
            for key, value in item.items():
                if key != "image_path":
                    index_item[key] = value
            
            dataset_index.append(index_item)
        
        # Save dataset index
        output_path = os.path.join(self.processed_dir, f"{dataset_name}_index.json")
        with open(output_path, 'w') as f:
            json.dump(dataset_index, f, indent=2)
        
        # Calculate statistics
        statistics = {
            "image_count": len(dataset_index),
            "has_annotations": any("annotations" in item for item in dataset_index),
            "has_splits": any("split" in item for item in dataset_index)
        }
        
        return {
            "output_path": output_path,
            "statistics": statistics,
            "dataset_type": "image"
        }
    
    def _process_generic_dataset(
        self,
        data: Any,
        dataset_name: str,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a generic dataset.
        
        Args:
            data: Dataset to process
            dataset_name: Name of the dataset
            config: Processing configuration
            
        Returns:
            Processing result
        """
        # For generic datasets, we just save metadata
        metadata = {
            "dataset_name": dataset_name,
            "processed_at": datetime.now().isoformat(),
            "data_type": str(type(data))
        }
        
        # Save metadata
        output_path = os.path.join(self.metadata_dir, f"{dataset_name}_metadata.json")
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "output_path": output_path,
            "statistics": metadata,
            "dataset_type": "generic"
        }
    
    def _perform_feature_selection(
        self,
        df: pd.DataFrame,
        config: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Perform feature selection.
        
        Args:
            df: DataFrame with features
            config: Processing configuration
            
        Returns:
            DataFrame with selected features
        """
        # Get numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) <= 1:
            # Not enough numeric columns for selection
            return df
        
        # Get feature selection method
        method = config["feature_selection"]["method"]
        max_features = min(config["feature_selection"]["max_features"], len(numeric_cols))
        
        if method not in self.feature_selection_pipelines:
            logger.warning(f"Feature selection method {method} not supported, skipping")
            return df
        
        try:
            # Configure selector
            selector = self.feature_selection_pipelines[method]
            
            if method in ["mutual_info", "f_regression"]:
                selector.k = max_features
            elif method == "pca":
                selector.n_components = max_features
            
            # Select a target column for supervised methods
            if method in ["mutual_info", "f_regression"]:
                # Use the first numeric column as target
                target_col = numeric_cols[0]
                feature_cols = numeric_cols[1:]
                
                if len(feature_cols) == 0:
                    # Not enough features
                    return df
                
                # Fit and transform
                X = df[feature_cols]
                y = df[target_col]
                
                selector.fit(X, y)
                
                # Get selected features
                if hasattr(selector, 'get_support'):
                    selected_features = X.columns[selector.get_support()].tolist()
                else:
                    # For PCA, keep all components
                    selected_features = feature_cols
                
                # Keep only selected features plus non-numeric and target
                keep_cols = [col for col in df.columns if col not in feature_cols or col in selected_features]
                return df[keep_cols]
            else:
                # Unsupervised methods like PCA
                X = df[numeric_cols]
                
                # Fit and transform
                transformed = selector.fit_transform(X)
                
                # Replace original features with transformed features
                transformed_df = pd.DataFrame(
                    transformed,
                    index=df.index,
                    columns=[f'component_{i}' for i in range(transformed.shape[1])]
                )
                
                # Combine with non-numeric columns
                non_numeric_cols = [col for col in df.columns if col not in numeric_cols]
                result_df = pd.concat([transformed_df, df[non_numeric_cols]], axis=1)
                
                return result_df
        except Exception as e:
            logger.error(f"Feature selection failed: {str(e)}")
            return df
    
    def get_processing_pipeline_for_offer(
        self,
        offer_id: str,
        dataset_name: str,
        dataset_type: str
    ) -> Dict[str, Any]:
        """
        Get processing pipeline configuration for a specific offer.
        
        Args:
            offer_id: ID of the offer
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            
        Returns:
            Processing pipeline configuration
        """
        # Map offer IDs to specific processing configurations
        offer_mappings = {
            "predictive_maintenance": {
                "preprocessing": {
                    "scaling_method": "robust",
                    "imputation_method": "knn",
                    "outlier_detection": "isolation_forest"
                },
                "feature_engineering": {
                    "enable_auto_feature_engineering": True,
                    "max_lag_features": 48,
                    "enable_cyclical_features": True,
                    "enable_interaction_features": True
                }
            },
            "anomaly_detection": {
                "preprocessing": {
                    "scaling_method": "robust",
                    "imputation_method": "knn",
                    "outlier_detection": "isolation_forest"
                },
                "feature_engineering": {
                    "enable_auto_feature_engineering": True,
                    "max_lag_features": 24,
                    "enable_cyclical_features": True,
                    "enable_interaction_features": False
                }
            },
            "energy_optimization": {
                "preprocessing": {
                    "scaling_method": "standard",
                    "imputation_method": "knn",
                    "outlier_detection": "iqr"
                },
                "feature_engineering": {
                    "enable_auto_feature_engineering": True,
                    "max_lag_features": 168,  # One week
                    "enable_cyclical_features": True,
                    "enable_interaction_features": True
                }
            },
            "quality_control": {
                "preprocessing": {
                    "scaling_method": "standard",
                    "imputation_method": "median",
                    "outlier_detection": "zscore"
                },
                "feature_engineering": {
                    "enable_auto_feature_engineering": True,
                    "max_lag_features": 12,
                    "enable_cyclical_features": False,
                    "enable_interaction_features": True
                }
            },
            "safety_monitoring": {
                "preprocessing": {
                    "scaling_method": "minmax",
                    "imputation_method": "constant",
                    "outlier_detection": "none"
                },
                "feature_engineering": {
                    "enable_auto_feature_engineering": False
                }
            }
        }
        
        # Find matching offer prefix
        pipeline_config = None
        for prefix, config in offer_mappings.items():
            if offer_id.startswith(prefix):
                pipeline_config = config
                break
        
        # Use default config if no match found
        if pipeline_config is None:
            pipeline_config = self.config.copy()
        
        # Adjust based on dataset type
        if dataset_type == "timeseries":
            # Ensure time series specific settings
            if "feature_engineering" not in pipeline_config:
                pipeline_config["feature_engineering"] = {}
            
            pipeline_config["feature_engineering"]["enable_cyclical_features"] = True
            pipeline_config["feature_engineering"]["max_lag_features"] = max(
                pipeline_config["feature_engineering"].get("max_lag_features", 24),
                24
            )
        elif dataset_type == "image":
            # Minimal processing for image datasets
            pipeline_config = {
                "preprocessing": {
                    "scaling_method": "none",
                    "imputation_method": "none",
                    "outlier_detection": "none"
                },
                "feature_engineering": {
                    "enable_auto_feature_engineering": False
                },
                "feature_selection": {
                    "enable_auto_selection": False
                }
            }
        
        # Add metadata
        pipeline_config["offer_id"] = offer_id
        pipeline_config["dataset_name"] = dataset_name
        pipeline_config["dataset_type"] = dataset_type
        pipeline_config["created_at"] = datetime.now().isoformat()
        
        return pipeline_config


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create data processing engine
    engine = DataProcessingEngine()
    
    # Process a dataset
    result = engine.process_dataset(
        dataset_path="path/to/dataset.csv",
        dataset_name="example_dataset"
    )
    
    print(f"Processing result: {json.dumps(result, indent=2)}")
    
    # Get processing pipeline for an offer
    pipeline = engine.get_processing_pipeline_for_offer(
        offer_id="predictive_maintenance_001",
        dataset_name="example_dataset",
        dataset_type="timeseries"
    )
    
    print(f"Processing pipeline: {json.dumps(pipeline, indent=2)}")
