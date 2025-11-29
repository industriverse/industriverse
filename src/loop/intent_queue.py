import sqlite3
import json
import time
import os

class IntentQueue:
    """
    Persistent Intent Queue backed by SQLite.
    Replaces the mock list implementation.
    """
    def __init__(self, db_path="intent_queue.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS intents
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      intent_text TEXT,
                      status TEXT,
                      timestamp REAL,
                      metadata TEXT)''')
        conn.commit()
        conn.close()

    def add(self, intent_text, metadata=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO intents (intent_text, status, timestamp, metadata) VALUES (?, ?, ?, ?)",
                  (intent_text, "PENDING", time.time(), json.dumps(metadata or {})))
        conn.commit()
        conn.close()

    def get_next(self):
        """Returns the next PENDING intent and marks it as PROCESSING."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Find oldest pending
        c.execute("SELECT id, intent_text, metadata FROM intents WHERE status='PENDING' ORDER BY timestamp ASC LIMIT 1")
        row = c.fetchone()
        
        if row:
            intent_id, text, meta_json = row
            # Mark as PROCESSING
            c.execute("UPDATE intents SET status='PROCESSING' WHERE id=?", (intent_id,))
            conn.commit()
            conn.close()
            return {
                "id": intent_id,
                "text": text,
                "metadata": json.loads(meta_json)
            }
        
        conn.close()
        return None

    def mark_complete(self, intent_id, result=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        meta = {"result": result} if result else {}
        c.execute("UPDATE intents SET status='COMPLETED', metadata=json_patch(metadata, ?) WHERE id=?",
                  (json.dumps(meta), intent_id)) # Note: json_patch might not be available in all sqlite versions, simplifying
        
        # Simplified update for compatibility
        c.execute("SELECT metadata FROM intents WHERE id=?", (intent_id,))
        current_meta = json.loads(c.fetchone()[0])
        if result:
            current_meta["result"] = result
            
        c.execute("UPDATE intents SET status='COMPLETED', metadata=? WHERE id=?",
                  (json.dumps(current_meta), intent_id))
        conn.commit()
        conn.close()

    def mark_failed(self, intent_id, error):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT metadata FROM intents WHERE id=?", (intent_id,))
        current_meta = json.loads(c.fetchone()[0])
        current_meta["error"] = error
        
        c.execute("UPDATE intents SET status='FAILED', metadata=? WHERE id=?",
                  (json.dumps(current_meta), intent_id))
        conn.commit()
        conn.close()

    def __len__(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM intents WHERE status='PENDING'")
        count = c.fetchone()[0]
        conn.close()
        return count
