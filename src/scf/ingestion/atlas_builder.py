import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any

class AtlasBuilder:
    """
    Constructs the Spatio-Temporal Index (Energy Atlas) from the Fossil Vault.
    Enables fast querying of physics states (Entropy, Power, Time).
    """
    def __init__(self, vault_dir: str, db_path: str = "energy_atlas.db"):
        self.vault_dir = Path(vault_dir)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Create Index Table
        c.execute('''CREATE TABLE IF NOT EXISTS atlas_index (
                        fossil_id TEXT PRIMARY KEY,
                        source TEXT,
                        timestamp REAL,
                        entropy_rate REAL,
                        file_path TEXT
                    )''')
        # Create Indices for fast lookup
        c.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON atlas_index (timestamp)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_entropy ON atlas_index (entropy_rate)')
        conn.commit()
        conn.close()

    def build_index(self):
        """
        Scans the Vault and populates the SQLite index.
        Idempotent: Skips existing IDs.
        """
        print(f"🗺️  Building Energy Atlas from {self.vault_dir}...")
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        count = 0
        for root, _, files in os.walk(self.vault_dir):
            for file in files:
                if file.endswith(".ndjson"):
                    file_path = Path(root) / file
                    self._index_file(file_path, c)
                    conn.commit() # Commit per file to be safe
                    count += 1
                    print(f"   Indexed {file}...", end="\r")
                    
        conn.close()
        print(f"\n✅ Atlas Built. Indexed {count} batch files.")

    def _index_file(self, file_path: Path, cursor):
        """Reads an NDJSON batch and inserts metadata."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    data = json.loads(line)
                    
                    # Extract Key Metrics
                    f_id = data.get('id')
                    source = data.get('source')
                    timestamp = data.get('timestamp', 0.0)
                    
                    # Try to get entropy from metadata
                    entropy = 0.0
                    meta = data.get('meta', {})
                    thermo = meta.get('thermodynamics', {})
                    if isinstance(thermo, dict):
                        entropy = thermo.get('entropy_rate', 0.0)
                    
                    # Insert (Ignore if exists)
                    cursor.execute('''INSERT OR IGNORE INTO atlas_index 
                                      (fossil_id, source, timestamp, entropy_rate, file_path)
                                      VALUES (?, ?, ?, ?, ?)''',
                                   (f_id, source, timestamp, entropy, str(file_path)))
        except Exception as e:
            print(f"   ⚠️ Error indexing {file_path.name}: {e}")

    def query(self, min_entropy: float = None, max_entropy: float = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find fossils matching constraints.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        query = "SELECT * FROM atlas_index WHERE 1=1"
        params = []
        
        if min_entropy is not None:
            query += " AND entropy_rate >= ?"
            params.append(min_entropy)

        if max_entropy is not None:
            query += " AND entropy_rate <= ?"
            params.append(max_entropy)
            
        query += " ORDER BY entropy_rate ASC LIMIT ?" # Prefer lower entropy (more ordered)
        params.append(limit)
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]

if __name__ == "__main__":
    # Example Usage
    import sys
    if len(sys.argv) > 1:
        builder = AtlasBuilder(sys.argv[1])
        builder.build_index()
    else:
        print("Usage: python atlas_builder.py <vault_dir>")
