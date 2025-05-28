"""
Synthetic Data Generator Agent for Industriverse Core AI Layer

This module implements the synthetic data generator agent for test case amplification
and data augmentation in the Core AI Layer.
"""

import logging
import json
import asyncio
import random
import numpy as np
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyntheticDataGeneratorAgent:
    """
    Implements the synthetic data generator agent for Core AI Layer.
    Provides test case amplification and data augmentation capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the synthetic data generator agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/synthetic_data_generator.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.dataset_registry = {}
        self.generator_registry = {}
        self.generation_history = []
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def register_dataset(self, dataset_id: str, dataset_type: str, dataset_schema: Dict[str, Any]) -> bool:
        """
        Register a dataset for synthetic data generation.
        
        Args:
            dataset_id: ID of the dataset
            dataset_type: Type of dataset (tabular, time_series, image, text)
            dataset_schema: Schema of the dataset
            
        Returns:
            True if successful, False otherwise
        """
        # Create dataset entry
        dataset = {
            "dataset_id": dataset_id,
            "dataset_type": dataset_type,
            "registration_timestamp": datetime.utcnow().isoformat(),
            "schema": dataset_schema,
            "generators": []
        }
        
        # Add to registry
        self.dataset_registry[dataset_id] = dataset
        
        logger.info(f"Registered dataset {dataset_id} of type {dataset_type}")
        
        return True
    
    async def register_generator(self, generator_id: str, generator_type: str, generator_config: Dict[str, Any]) -> bool:
        """
        Register a data generator.
        
        Args:
            generator_id: ID of the generator
            generator_type: Type of generator
            generator_config: Generator configuration
            
        Returns:
            True if successful, False otherwise
        """
        # Create generator entry
        generator = {
            "generator_id": generator_id,
            "generator_type": generator_type,
            "registration_timestamp": datetime.utcnow().isoformat(),
            "config": generator_config,
            "status": "active"
        }
        
        # Add to registry
        self.generator_registry[generator_id] = generator
        
        logger.info(f"Registered generator {generator_id} of type {generator_type}")
        
        return True
    
    async def link_generator_to_dataset(self, generator_id: str, dataset_id: str) -> bool:
        """
        Link a generator to a dataset.
        
        Args:
            generator_id: ID of the generator
            dataset_id: ID of the dataset
            
        Returns:
            True if successful, False otherwise
        """
        if generator_id not in self.generator_registry:
            logger.warning(f"Generator not found: {generator_id}")
            return False
            
        if dataset_id not in self.dataset_registry:
            logger.warning(f"Dataset not found: {dataset_id}")
            return False
            
        # Add generator to dataset
        self.dataset_registry[dataset_id]["generators"].append(generator_id)
        
        logger.info(f"Linked generator {generator_id} to dataset {dataset_id}")
        
        return True
    
    async def generate_synthetic_data(self, dataset_id: str, generator_id: str, 
                                     sample_count: int, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate synthetic data.
        
        Args:
            dataset_id: ID of the dataset
            generator_id: ID of the generator
            sample_count: Number of samples to generate
            config_overrides: Configuration overrides (optional)
            
        Returns:
            Generated data
        """
        if dataset_id not in self.dataset_registry:
            logger.warning(f"Dataset not found: {dataset_id}")
            return {"success": False, "error": "Dataset not found"}
            
        if generator_id not in self.generator_registry:
            logger.warning(f"Generator not found: {generator_id}")
            return {"success": False, "error": "Generator not found"}
            
        dataset = self.dataset_registry[dataset_id]
        generator = self.generator_registry[generator_id]
        
        # Check if generator is linked to dataset
        if generator_id not in dataset["generators"]:
            logger.warning(f"Generator {generator_id} is not linked to dataset {dataset_id}")
            return {"success": False, "error": "Generator not linked to dataset"}
        
        logger.info(f"Generating {sample_count} synthetic samples for dataset {dataset_id} using generator {generator_id}")
        
        try:
            # Generate data based on dataset type
            dataset_type = dataset["dataset_type"]
            
            if dataset_type == "tabular":
                data = await self._generate_tabular_data(dataset, generator, sample_count, config_overrides)
            elif dataset_type == "time_series":
                data = await self._generate_time_series_data(dataset, generator, sample_count, config_overrides)
            elif dataset_type == "image":
                data = await self._generate_image_data(dataset, generator, sample_count, config_overrides)
            elif dataset_type == "text":
                data = await self._generate_text_data(dataset, generator, sample_count, config_overrides)
            else:
                logger.warning(f"Unsupported dataset type: {dataset_type}")
                return {"success": False, "error": f"Unsupported dataset type: {dataset_type}"}
            
            # Record generation
            generation_id = f"gen-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            generation = {
                "generation_id": generation_id,
                "dataset_id": dataset_id,
                "generator_id": generator_id,
                "timestamp": datetime.utcnow().isoformat(),
                "sample_count": sample_count,
                "config_overrides": config_overrides or {}
            }
            
            self.generation_history.append(generation)
            
            # Keep history size manageable
            max_history = self.config.get("max_generation_history", 1000)
            if len(self.generation_history) > max_history:
                self.generation_history = self.generation_history[-max_history:]
            
            logger.info(f"Generated {sample_count} synthetic samples successfully")
            
            return {
                "success": True,
                "generation_id": generation_id,
                "data": data
            }
        except Exception as e:
            logger.error(f"Error generating synthetic data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_tabular_data(self, dataset: Dict[str, Any], generator: Dict[str, Any], 
                                    sample_count: int, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate tabular data.
        
        Args:
            dataset: Dataset information
            generator: Generator information
            sample_count: Number of samples to generate
            config_overrides: Configuration overrides (optional)
            
        Returns:
            Generated data
        """
        schema = dataset["schema"]
        columns = schema.get("columns", [])
        
        if not columns:
            raise ValueError("Dataset schema does not define columns")
        
        # Generate data for each column
        data = {}
        
        for column in columns:
            column_name = column["name"]
            column_type = column["type"]
            
            # Generate column data based on type
            if column_type == "numeric":
                min_value = column.get("min", 0)
                max_value = column.get("max", 100)
                
                # Apply overrides if provided
                if config_overrides and "columns" in config_overrides:
                    col_override = next((c for c in config_overrides["columns"] if c["name"] == column_name), None)
                    if col_override:
                        min_value = col_override.get("min", min_value)
                        max_value = col_override.get("max", max_value)
                
                data[column_name] = np.random.uniform(min_value, max_value, sample_count).tolist()
                
            elif column_type == "categorical":
                categories = column.get("categories", ["A", "B", "C"])
                weights = column.get("weights", None)
                
                # Apply overrides if provided
                if config_overrides and "columns" in config_overrides:
                    col_override = next((c for c in config_overrides["columns"] if c["name"] == column_name), None)
                    if col_override:
                        categories = col_override.get("categories", categories)
                        weights = col_override.get("weights", weights)
                
                data[column_name] = np.random.choice(categories, size=sample_count, p=weights).tolist()
                
            elif column_type == "boolean":
                prob_true = column.get("prob_true", 0.5)
                
                # Apply overrides if provided
                if config_overrides and "columns" in config_overrides:
                    col_override = next((c for c in config_overrides["columns"] if c["name"] == column_name), None)
                    if col_override:
                        prob_true = col_override.get("prob_true", prob_true)
                
                data[column_name] = np.random.choice([True, False], size=sample_count, p=[prob_true, 1-prob_true]).tolist()
                
            elif column_type == "datetime":
                start_date = column.get("start_date", "2020-01-01T00:00:00")
                end_date = column.get("end_date", "2023-01-01T00:00:00")
                
                # Apply overrides if provided
                if config_overrides and "columns" in config_overrides:
                    col_override = next((c for c in config_overrides["columns"] if c["name"] == column_name), None)
                    if col_override:
                        start_date = col_override.get("start_date", start_date)
                        end_date = col_override.get("end_date", end_date)
                
                start_ts = datetime.fromisoformat(start_date).timestamp()
                end_ts = datetime.fromisoformat(end_date).timestamp()
                
                random_ts = np.random.uniform(start_ts, end_ts, sample_count)
                data[column_name] = [datetime.fromtimestamp(ts).isoformat() for ts in random_ts]
            
            else:
                logger.warning(f"Unsupported column type: {column_type}")
                data[column_name] = [""] * sample_count
        
        return {
            "type": "tabular",
            "columns": list(data.keys()),
            "data": data
        }
    
    async def _generate_time_series_data(self, dataset: Dict[str, Any], generator: Dict[str, Any], 
                                        sample_count: int, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate time series data.
        
        Args:
            dataset: Dataset information
            generator: Generator information
            sample_count: Number of samples to generate
            config_overrides: Configuration overrides (optional)
            
        Returns:
            Generated data
        """
        schema = dataset["schema"]
        series_length = schema.get("series_length", 100)
        variables = schema.get("variables", [])
        
        if not variables:
            raise ValueError("Dataset schema does not define variables")
        
        # Apply overrides if provided
        if config_overrides:
            series_length = config_overrides.get("series_length", series_length)
        
        # Generate time series for each sample
        samples = []
        
        for i in range(sample_count):
            sample = {
                "sample_id": f"sample-{i}",
                "timestamp": datetime.utcnow().isoformat(),
                "series": {}
            }
            
            # Generate time points
            time_points = np.arange(series_length)
            sample["series"]["time"] = time_points.tolist()
            
            # Generate each variable
            for variable in variables:
                var_name = variable["name"]
                var_type = variable.get("type", "random_walk")
                
                # Generate variable data based on type
                if var_type == "random_walk":
                    # Random walk with drift
                    drift = variable.get("drift", 0)
                    volatility = variable.get("volatility", 1)
                    
                    # Apply overrides if provided
                    if config_overrides and "variables" in config_overrides:
                        var_override = next((v for v in config_overrides["variables"] if v["name"] == var_name), None)
                        if var_override:
                            drift = var_override.get("drift", drift)
                            volatility = var_override.get("volatility", volatility)
                    
                    # Generate random walk
                    steps = np.random.normal(drift, volatility, series_length)
                    walk = np.cumsum(steps)
                    
                    sample["series"][var_name] = walk.tolist()
                    
                elif var_type == "sine_wave":
                    # Sine wave with noise
                    amplitude = variable.get("amplitude", 1)
                    frequency = variable.get("frequency", 0.1)
                    noise_level = variable.get("noise_level", 0.1)
                    
                    # Apply overrides if provided
                    if config_overrides and "variables" in config_overrides:
                        var_override = next((v for v in config_overrides["variables"] if v["name"] == var_name), None)
                        if var_override:
                            amplitude = var_override.get("amplitude", amplitude)
                            frequency = var_override.get("frequency", frequency)
                            noise_level = var_override.get("noise_level", noise_level)
                    
                    # Generate sine wave with noise
                    wave = amplitude * np.sin(2 * np.pi * frequency * time_points)
                    noise = np.random.normal(0, noise_level, series_length)
                    
                    sample["series"][var_name] = (wave + noise).tolist()
                    
                elif var_type == "ar_process":
                    # Autoregressive process
                    ar_params = variable.get("ar_params", [0.8])
                    sigma = variable.get("sigma", 1)
                    
                    # Apply overrides if provided
                    if config_overrides and "variables" in config_overrides:
                        var_override = next((v for v in config_overrides["variables"] if v["name"] == var_name), None)
                        if var_override:
                            ar_params = var_override.get("ar_params", ar_params)
                            sigma = var_override.get("sigma", sigma)
                    
                    # Generate AR process
                    ar_order = len(ar_params)
                    series = np.zeros(series_length)
                    
                    # Initialize with random values
                    series[:ar_order] = np.random.normal(0, sigma, ar_order)
                    
                    # Generate the rest of the series
                    for t in range(ar_order, series_length):
                        series[t] = np.sum([ar_params[i] * series[t-i-1] for i in range(ar_order)]) + np.random.normal(0, sigma)
                    
                    sample["series"][var_name] = series.tolist()
                    
                else:
                    logger.warning(f"Unsupported variable type: {var_type}")
                    sample["series"][var_name] = np.zeros(series_length).tolist()
            
            samples.append(sample)
        
        return {
            "type": "time_series",
            "series_length": series_length,
            "variables": [v["name"] for v in variables],
            "samples": samples
        }
    
    async def _generate_image_data(self, dataset: Dict[str, Any], generator: Dict[str, Any], 
                                  sample_count: int, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate image data.
        
        Args:
            dataset: Dataset information
            generator: Generator information
            sample_count: Number of samples to generate
            config_overrides: Configuration overrides (optional)
            
        Returns:
            Generated data
        """
        schema = dataset["schema"]
        width = schema.get("width", 28)
        height = schema.get("height", 28)
        channels = schema.get("channels", 1)
        
        # Apply overrides if provided
        if config_overrides:
            width = config_overrides.get("width", width)
            height = config_overrides.get("height", height)
            channels = config_overrides.get("channels", channels)
        
        # Generate images
        images = []
        
        for i in range(sample_count):
            # In a real implementation, this would use more sophisticated
            # image generation techniques (e.g., GANs, diffusion models)
            
            # For now, generate random noise
            if channels == 1:
                # Grayscale
                image = np.random.rand(height, width).tolist()
            else:
                # RGB
                image = np.random.rand(height, width, channels).tolist()
            
            images.append({
                "image_id": f"image-{i}",
                "timestamp": datetime.utcnow().isoformat(),
                "width": width,
                "height": height,
                "channels": channels,
                "data": image
            })
        
        return {
            "type": "image",
            "width": width,
            "height": height,
            "channels": channels,
            "images": images
        }
    
    async def _generate_text_data(self, dataset: Dict[str, Any], generator: Dict[str, Any], 
                                 sample_count: int, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate text data.
        
        Args:
            dataset: Dataset information
            generator: Generator information
            sample_count: Number of samples to generate
            config_overrides: Configuration overrides (optional)
            
        Returns:
            Generated data
        """
        schema = dataset["schema"]
        text_type = schema.get("text_type", "sentence")
        
        # Apply overrides if provided
        if config_overrides:
            text_type = config_overrides.get("text_type", text_type)
        
        # Generate text samples
        texts = []
        
        for i in range(sample_count):
            # In a real implementation, this would use more sophisticated
            # text generation techniques (e.g., language models)
            
            # For now, generate placeholder text
            if text_type == "sentence":
                length = random.randint(5, 15)
                text = " ".join(["word"] * length)
            elif text_type == "paragraph":
                sentences = random.randint(3, 8)
                text = ". ".join(["This is a sample sentence"] * sentences) + "."
            elif text_type == "document":
                paragraphs = random.randint(2, 5)
                text = "\n\n".join(["This is a sample paragraph."] * paragraphs)
            else:
                text = "Sample text"
            
            texts.append({
                "text_id": f"text-{i}",
                "timestamp": datetime.utcnow().isoformat(),
                "text_type": text_type,
                "text": text
            })
        
        return {
            "type": "text",
            "text_type": text_type,
            "texts": texts
        }
    
    async def amplify_test_cases(self, test_cases: List[Dict[str, Any]], amplification_factor: int, 
                                variation_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Amplify test cases by generating variations.
        
        Args:
            test_cases: Original test cases
            amplification_factor: Number of variations to generate per test case
            variation_config: Configuration for variations
            
        Returns:
            Amplified test cases
        """
        if not test_cases:
            logger.warning("No test cases provided for amplification")
            return {"success": False, "error": "No test cases provided"}
        
        logger.info(f"Amplifying {len(test_cases)} test cases with factor {amplification_factor}")
        
        try:
            # Determine test case type
            test_type = self._determine_test_case_type(test_cases[0])
            
            # Generate variations based on type
            if test_type == "tabular":
                amplified = await self._amplify_tabular_test_cases(test_cases, amplification_factor, variation_config)
            elif test_type == "time_series":
                amplified = await self._amplify_time_series_test_cases(test_cases, amplification_factor, variation_config)
            elif test_type == "image":
                amplified = await self._amplify_image_test_cases(test_cases, amplification_factor, variation_config)
            elif test_type == "text":
                amplified = await self._amplify_text_test_cases(test_cases, amplification_factor, variation_config)
            else:
                logger.warning(f"Unsupported test case type: {test_type}")
                return {"success": False, "error": f"Unsupported test case type: {test_type}"}
            
            logger.info(f"Generated {len(amplified)} amplified test cases")
            
            return {
                "success": True,
                "original_count": len(test_cases),
                "amplified_count": len(amplified),
                "amplification_factor": amplification_factor,
                "test_cases": amplified
            }
        except Exception as e:
            logger.error(f"Error amplifying test cases: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_test_case_type(self, test_case: Dict[str, Any]) -> str:
        """
        Determine the type of a test case.
        
        Args:
            test_case: Test case data
            
        Returns:
            Test case type
        """
        if "columns" in test_case and "data" in test_case:
            return "tabular"
        elif "series" in test_case:
            return "time_series"
        elif "width" in test_case and "height" in test_case and "data" in test_case:
            return "image"
        elif "text" in test_case:
            return "text"
        else:
            return "unknown"
    
    async def _amplify_tabular_test_cases(self, test_cases: List[Dict[str, Any]], amplification_factor: int, 
                                         variation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Amplify tabular test cases.
        
        Args:
            test_cases: Original test cases
            amplification_factor: Number of variations to generate per test case
            variation_config: Configuration for variations
            
        Returns:
            Amplified test cases
        """
        amplified = []
        
        # Add original test cases
        amplified.extend(test_cases)
        
        # Generate variations
        for test_case in test_cases:
            columns = test_case["columns"]
            data = test_case["data"]
            
            for i in range(amplification_factor):
                # Create a variation
                variation = {
                    "columns": columns.copy(),
                    "data": {}
                }
                
                # Vary each column
                for column in columns:
                    original_values = data[column]
                    
                    # Get column variation config
                    column_config = next((c for c in variation_config.get("columns", []) if c["name"] == column), None)
                    
                    if not column_config:
                        # No specific config, copy original
                        variation["data"][column] = original_values.copy()
                        continue
                    
                    # Apply variation based on type
                    variation_type = column_config.get("variation_type", "noise")
                    
                    if variation_type == "noise":
                        # Add random noise
                        noise_level = column_config.get("noise_level", 0.1)
                        
                        # Check if numeric
                        if all(isinstance(v, (int, float)) for v in original_values):
                            # Add noise to numeric values
                            values = np.array(original_values)
                            scale = np.abs(values) * noise_level
                            noise = np.random.normal(0, scale)
                            variation["data"][column] = (values + noise).tolist()
                        else:
                            # Non-numeric, copy original
                            variation["data"][column] = original_values.copy()
                    
                    elif variation_type == "shuffle":
                        # Shuffle a percentage of values
                        shuffle_percent = column_config.get("shuffle_percent", 10)
                        
                        values = original_values.copy()
                        count = len(values)
                        shuffle_count = int(count * shuffle_percent / 100)
                        
                        if shuffle_count > 0:
                            # Select indices to shuffle
                            indices = np.random.choice(count, shuffle_count, replace=False)
                            
                            # Shuffle selected values
                            shuffled_values = [values[i] for i in indices]
                            np.random.shuffle(shuffled_values)
                            
                            # Replace values
                            for idx, new_value in zip(indices, shuffled_values):
                                values[idx] = new_value
                        
                        variation["data"][column] = values
                    
                    elif variation_type == "replace":
                        # Replace a percentage of values
                        replace_percent = column_config.get("replace_percent", 10)
                        replacement_values = column_config.get("replacement_values", [])
                        
                        values = original_values.copy()
                        count = len(values)
                        replace_count = int(count * replace_percent / 100)
                        
                        if replace_count > 0 and replacement_values:
                            # Select indices to replace
                            indices = np.random.choice(count, replace_count, replace=False)
                            
                            # Replace values
                            for idx in indices:
                                values[idx] = random.choice(replacement_values)
                        
                        variation["data"][column] = values
                    
                    else:
                        # Unknown variation type, copy original
                        variation["data"][column] = original_values.copy()
                
                amplified.append(variation)
        
        return amplified
    
    async def _amplify_time_series_test_cases(self, test_cases: List[Dict[str, Any]], amplification_factor: int, 
                                            variation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Amplify time series test cases.
        
        Args:
            test_cases: Original test cases
            amplification_factor: Number of variations to generate per test case
            variation_config: Configuration for variations
            
        Returns:
            Amplified test cases
        """
        amplified = []
        
        # Add original test cases
        amplified.extend(test_cases)
        
        # Generate variations
        for test_case in test_cases:
            series = test_case["series"]
            
            for i in range(amplification_factor):
                # Create a variation
                variation = {
                    "sample_id": f"{test_case.get('sample_id', 'sample')}-var-{i}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "series": {}
                }
                
                # Copy time points
                if "time" in series:
                    variation["series"]["time"] = series["time"].copy()
                
                # Vary each variable
                for var_name, values in series.items():
                    if var_name == "time":
                        continue
                    
                    # Get variable variation config
                    var_config = next((v for v in variation_config.get("variables", []) if v["name"] == var_name), None)
                    
                    if not var_config:
                        # No specific config, copy original
                        variation["series"][var_name] = values.copy()
                        continue
                    
                    # Apply variation based on type
                    variation_type = var_config.get("variation_type", "noise")
                    
                    if variation_type == "noise":
                        # Add random noise
                        noise_level = var_config.get("noise_level", 0.1)
                        
                        values_array = np.array(values)
                        scale = np.abs(values_array) * noise_level
                        noise = np.random.normal(0, scale)
                        variation["series"][var_name] = (values_array + noise).tolist()
                    
                    elif variation_type == "shift":
                        # Shift the series
                        shift_amount = var_config.get("shift_amount", 0)
                        
                        values_array = np.array(values)
                        variation["series"][var_name] = (values_array + shift_amount).tolist()
                    
                    elif variation_type == "scale":
                        # Scale the series
                        scale_factor = var_config.get("scale_factor", 1)
                        
                        values_array = np.array(values)
                        variation["series"][var_name] = (values_array * scale_factor).tolist()
                    
                    elif variation_type == "trend":
                        # Add a trend
                        trend_slope = var_config.get("trend_slope", 0.01)
                        
                        values_array = np.array(values)
                        trend = np.arange(len(values_array)) * trend_slope
                        variation["series"][var_name] = (values_array + trend).tolist()
                    
                    else:
                        # Unknown variation type, copy original
                        variation["series"][var_name] = values.copy()
                
                amplified.append(variation)
        
        return amplified
    
    async def _amplify_image_test_cases(self, test_cases: List[Dict[str, Any]], amplification_factor: int, 
                                       variation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Amplify image test cases.
        
        Args:
            test_cases: Original test cases
            amplification_factor: Number of variations to generate per test case
            variation_config: Configuration for variations
            
        Returns:
            Amplified test cases
        """
        amplified = []
        
        # Add original test cases
        amplified.extend(test_cases)
        
        # Generate variations
        for test_case in test_cases:
            width = test_case["width"]
            height = test_case["height"]
            channels = test_case.get("channels", 1)
            image_data = test_case["data"]
            
            for i in range(amplification_factor):
                # Create a variation
                variation = {
                    "image_id": f"{test_case.get('image_id', 'image')}-var-{i}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "width": width,
                    "height": height,
                    "channels": channels
                }
                
                # Convert to numpy array for easier manipulation
                image_array = np.array(image_data)
                
                # Apply variations based on config
                variation_types = variation_config.get("variation_types", ["noise"])
                
                for variation_type in variation_types:
                    if variation_type == "noise":
                        # Add random noise
                        noise_level = variation_config.get("noise_level", 0.1)
                        noise = np.random.normal(0, noise_level, image_array.shape)
                        image_array = np.clip(image_array + noise, 0, 1)
                    
                    elif variation_type == "brightness":
                        # Adjust brightness
                        brightness_shift = variation_config.get("brightness_shift", 0)
                        image_array = np.clip(image_array + brightness_shift, 0, 1)
                    
                    elif variation_type == "contrast":
                        # Adjust contrast
                        contrast_factor = variation_config.get("contrast_factor", 1)
                        mean = np.mean(image_array)
                        image_array = np.clip(mean + contrast_factor * (image_array - mean), 0, 1)
                
                variation["data"] = image_array.tolist()
                amplified.append(variation)
        
        return amplified
    
    async def _amplify_text_test_cases(self, test_cases: List[Dict[str, Any]], amplification_factor: int, 
                                      variation_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Amplify text test cases.
        
        Args:
            test_cases: Original test cases
            amplification_factor: Number of variations to generate per test case
            variation_config: Configuration for variations
            
        Returns:
            Amplified test cases
        """
        amplified = []
        
        # Add original test cases
        amplified.extend(test_cases)
        
        # Generate variations
        for test_case in test_cases:
            text = test_case["text"]
            text_type = test_case.get("text_type", "text")
            
            for i in range(amplification_factor):
                # Create a variation
                variation = {
                    "text_id": f"{test_case.get('text_id', 'text')}-var-{i}",
                    "timestamp": datetime.utcnow().isoformat(),
                    "text_type": text_type
                }
                
                # Apply variations based on config
                variation_types = variation_config.get("variation_types", ["word_replacement"])
                
                # Start with original text
                varied_text = text
                
                for variation_type in variation_types:
                    if variation_type == "word_replacement":
                        # Replace random words
                        replace_percent = variation_config.get("replace_percent", 10)
                        
                        words = varied_text.split()
                        count = len(words)
                        replace_count = max(1, int(count * replace_percent / 100))
                        
                        # Select indices to replace
                        indices = np.random.choice(count, replace_count, replace=False)
                        
                        # Replace words
                        for idx in indices:
                            words[idx] = "REPLACED"
                        
                        varied_text = " ".join(words)
                    
                    elif variation_type == "character_noise":
                        # Add character-level noise
                        noise_percent = variation_config.get("noise_percent", 5)
                        
                        chars = list(varied_text)
                        count = len(chars)
                        noise_count = max(1, int(count * noise_percent / 100))
                        
                        # Select indices to modify
                        indices = np.random.choice(count, noise_count, replace=False)
                        
                        # Modify characters
                        for idx in indices:
                            chars[idx] = random.choice("abcdefghijklmnopqrstuvwxyz")
                        
                        varied_text = "".join(chars)
                
                variation["text"] = varied_text
                amplified.append(variation)
        
        return amplified
    
    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get a dataset.
        
        Args:
            dataset_id: ID of the dataset
            
        Returns:
            Dataset data
        """
        if dataset_id not in self.dataset_registry:
            logger.warning(f"Dataset not found: {dataset_id}")
            return {}
            
        return self.dataset_registry[dataset_id]
    
    def get_generator(self, generator_id: str) -> Dict[str, Any]:
        """
        Get a generator.
        
        Args:
            generator_id: ID of the generator
            
        Returns:
            Generator data
        """
        if generator_id not in self.generator_registry:
            logger.warning(f"Generator not found: {generator_id}")
            return {}
            
        return self.generator_registry[generator_id]
    
    def get_generation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get generation history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of generation history items
        """
        return self.generation_history[-limit:]


# Example usage
if __name__ == "__main__":
    async def main():
        # Create a synthetic data generator agent
        generator = SyntheticDataGeneratorAgent()
        
        # Register a dataset
        await generator.register_dataset("manufacturing_defects", "tabular", {
            "columns": [
                {"name": "temperature", "type": "numeric", "min": 50, "max": 100},
                {"name": "pressure", "type": "numeric", "min": 10, "max": 30},
                {"name": "defect", "type": "boolean", "prob_true": 0.2}
            ]
        })
        
        # Register a generator
        await generator.register_generator("tabular_generator", "tabular", {
            "method": "random"
        })
        
        # Link generator to dataset
        await generator.link_generator_to_dataset("tabular_generator", "manufacturing_defects")
        
        # Generate synthetic data
        result = await generator.generate_synthetic_data("manufacturing_defects", "tabular_generator", 10)
        
        if result["success"]:
            print(f"Generated {len(result['data']['data']['temperature'])} samples")
            
            # Amplify test cases
            test_cases = [
                {
                    "columns": result["data"]["columns"],
                    "data": {col: result["data"]["data"][col][:5] for col in result["data"]["columns"]}
                }
            ]
            
            amplified = await generator.amplify_test_cases(test_cases, 3, {
                "columns": [
                    {"name": "temperature", "variation_type": "noise", "noise_level": 0.05},
                    {"name": "pressure", "variation_type": "noise", "noise_level": 0.1}
                ]
            })
            
            if amplified["success"]:
                print(f"Amplified to {amplified['amplified_count']} test cases")
            else:
                print(f"Amplification failed: {amplified['error']}")
        else:
            print(f"Generation failed: {result['error']}")
    
    asyncio.run(main())
