from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import pandas as pd

class DataConnector(ABC):
    """
    Abstract base class for all data connectors.
    """
    
    @abstractmethod
    def connect(self, connection_string: str, **kwargs) -> bool:
        """Establish connection to the data source."""
        pass
        
    @abstractmethod
    def fetch_data(self, query: str, **kwargs) -> pd.DataFrame:
        """Fetch data based on a query or file path."""
        pass
        
    @abstractmethod
    def disconnect(self):
        """Close connection."""
        pass
