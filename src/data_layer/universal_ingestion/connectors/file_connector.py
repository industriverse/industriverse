import pandas as pd
import os
from .base import DataConnector

class FileConnector(DataConnector):
    """
    Connector for local files (CSV, JSON, Excel, Parquet).
    """
    
    def __init__(self):
        self.file_path = None
        
    def connect(self, connection_string: str, **kwargs) -> bool:
        """
        For files, connection_string is the file path.
        """
        if os.path.exists(connection_string):
            self.file_path = connection_string
            return True
        return False
        
    def fetch_data(self, query: str = None, **kwargs) -> pd.DataFrame:
        """
        Reads the file. Query is ignored for files unless specific logic added.
        """
        if not self.file_path:
            raise ValueError("Not connected to a file.")
            
        ext = os.path.splitext(self.file_path)[1].lower()
        
        if ext == '.csv':
            return pd.read_csv(self.file_path, **kwargs)
        elif ext == '.json':
            return pd.read_json(self.file_path, **kwargs)
        elif ext in ['.xls', '.xlsx']:
            return pd.read_excel(self.file_path, **kwargs)
        elif ext == '.parquet':
            return pd.read_parquet(self.file_path, **kwargs)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
            
    def disconnect(self):
        self.file_path = None
