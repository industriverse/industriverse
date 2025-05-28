# data_layer_client_interface.py

from abc import ABC, abstractmethod
from typing import Any, Dict

from .ml_models_schemas import DataSourceConfig

class DataLayerClientInterface(ABC):
    """
    Abstract Base Class defining the interface for a Data Layer client.
    Machine learning services will use this interface to interact with the Data Layer
    for fetching training, evaluation, and prediction datasets.
    """

    @abstractmethod
    async def load_data(self, config: DataSourceConfig) -> Any:
        """
        Loads data from the source specified in the DataSourceConfig.

        Args:
            config: Configuration detailing the data source, type, path, and access parameters.

        Returns:
            The loaded data in a format suitable for ML processing (e.g., pandas DataFrame, Spark DataFrame, NumPy array).
        
        Raises:
            NotImplementedError: If the method is not implemented by a concrete class.
            # Specific exceptions related to data access, e.g., DataNotFoundError, ConnectionError.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_data_schema(self, config: DataSourceConfig) -> Dict[str, Any]:
        """
        Retrieves the schema or metadata for the specified data source.

        Args:
            config: Configuration detailing the data source.

        Returns:
            A dictionary representing the data schema (e.g., column names, data types).
        
        Raises:
            NotImplementedError: If the method is not implemented by a concrete class.
        """
        raise NotImplementedError

# Example concrete implementation (placeholder)
# class ConcreteDataLayerClient(DataLayerClientInterface):
#     async def load_data(self, config: DataSourceConfig) -> Any:
#         print(f"[ConcreteDataLayerClient] Loading data from: {config.path} (type: {config.type})")
#         # Simulate data loading
#         if config.type == "csv":
#             # import pandas as pd
#             # return pd.read_csv(config.path)
#             return {"features": [[1,2],[3,4]], "target": [0,1]} # Placeholder
#         return None

#     async def get_data_schema(self, config: DataSourceConfig) -> Dict[str, Any]:
#         print(f"[ConcreteDataLayerClient] Getting schema for: {config.path}")
#         return {"column1": "int", "column2": "string"}

