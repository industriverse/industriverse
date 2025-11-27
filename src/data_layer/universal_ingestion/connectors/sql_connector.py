import pandas as pd
from sqlalchemy import create_engine, text
from .base import DataConnector

class SQLConnector(DataConnector):
    """
    Connector for SQL databases via SQLAlchemy.
    """
    
    def __init__(self):
        self.engine = None
        
    def connect(self, connection_string: str, **kwargs) -> bool:
        """
        connection_string: SQLAlchemy compatible URI (e.g., postgresql://user:pass@host/db)
        """
        try:
            self.engine = create_engine(connection_string)
            # Test connection
            with self.engine.connect() as conn:
                pass
            return True
        except Exception as e:
            print(f"SQL Connection failed: {e}")
            return False
            
    def fetch_data(self, query: str, **kwargs) -> pd.DataFrame:
        """
        Executes SQL query and returns DataFrame.
        """
        if not self.engine:
            raise ValueError("Not connected to a database.")
            
        with self.engine.connect() as conn:
            return pd.read_sql(text(query), conn)
            
    def disconnect(self):
        if self.engine:
            self.engine.dispose()
            self.engine = None
