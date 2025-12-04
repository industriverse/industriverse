import os
import json
import sqlite3
from pathlib import Path

class AtlasBuilder:
    """
    The Memory Palace.
    Indexes Fossils into a queryable Spatio-Temporal Database (The Energy Atlas).
    """
    def __init__(self, vault_dir: str, atlas_dir: str):
        self.vault_dir = Path(vault_dir)
        self.atlas_path = Path(atlas_dir) / "energy_atlas.db"
        self._init_db()
        print(f"🗺️  Atlas Builder Online. Target: {self.atlas_path}")

    def _init_db(self):
        conn = sqlite3.connect(self.atlas_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS fossils
                     (id TEXT PRIMARY KEY, source TEXT, timestamp REAL, data_json TEXT)''')
        c.execute('''CREATE INDEX IF NOT EXISTS idx_time ON fossils (timestamp)''')
        conn.commit()
        conn.close()

    def build(self):
        """
        Scans the Fossil Vault and updates the Index.
        """
        files = list(self.vault_dir.glob("*.ndjson"))
        print(f"   Found {len(files)} fossil batches.")
        
        conn = sqlite3.connect(self.atlas_path)
        c = conn.cursor()
        
        count = 0
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        if not line.strip(): continue
                        try:
                            fossil = json.loads(line)
                            c.execute("INSERT OR IGNORE INTO fossils VALUES (?, ?, ?, ?)",
                                      (fossil['id'], fossil['source'], fossil.get('timestamp', 0), json.dumps(fossil['data'])))
                            count += 1
                        except Exception as e:
                            print(f"   ⚠️ Error indexing fossil in {file_path.name}: {e}")
            except Exception as e:
                print(f"   ❌ Error reading file {file_path.name}: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Atlas Updated. Indexed {count} fossils.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        builder = AtlasBuilder(sys.argv[1], sys.argv[2])
        builder.build()
    else:
        print("Usage: python build_atlas.py <vault_dir> <atlas_dir>")
