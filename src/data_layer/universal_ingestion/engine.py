import pandas as pd
from typing import Dict, Any, Optional
from .connectors.file_connector import FileConnector
from .connectors.sql_connector import SQLConnector

class UniversalIngestionEngine:
    """
    Orchestrates data ingestion from various sources.
    """
    
    def __init__(self):
        self.connectors = {
            "file": FileConnector(),
            "sql": SQLConnector()
        }
        
    def ingest_data(self, source_type: str, connection_string: str, query: Optional[str] = None) -> pd.DataFrame:
        """
        Ingest data from a source.
        
        Args:
            source_type: 'file' or 'sql'
            connection_string: File path or DB URI
            query: SQL query (optional for files)
        """
        if source_type not in self.connectors:
            raise ValueError(f"Unknown source type: {source_type}")
            
        connector = self.connectors[source_type]
        
        try:
            if connector.connect(connection_string):
                df = connector.fetch_data(query)
                connector.disconnect()
                return df
            else:
                raise ConnectionError(f"Failed to connect to {connection_string}")
        except Exception as e:
            connector.disconnect()
            raise e
            
    def normalize_to_energy_map(self, df: pd.DataFrame, mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Convert DataFrame to Energy Map format.
        mapping: {"node_id": "col_name", "voltage": "col_name", ...}
        """
        nodes = {}
        for _, row in df.iterrows():
            node_id = row.get(mapping.get("node_id", "id"), f"node_{_}")
            nodes[node_id] = {
                "node_id": node_id,
                "electrical": {
                    "voltage_max": row.get(mapping.get("voltage", "voltage"), 1.0),
                    # Default other fields or map them
                },
                "metadata": row.to_dict()
            }
            
        return {
            "node_count": len(nodes),
            "nodes": nodes
        }
