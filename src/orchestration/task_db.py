import sqlite3
import json
import time
from datetime import datetime

class TaskDB:
    def __init__(self, db_path="data/orchestration/tasks.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        # Enhanced Schema for Trinity Architecture
        c.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            status TEXT,
            dependencies TEXT, -- JSON list
            source TEXT,       -- capsule:// or local path
            
            -- Chronos
            schedule TEXT,
            next_run_at REAL,
            
            -- Kairos
            energy_cost_est REAL,
            negentropy_value REAL,
            max_bid_price REAL,
            hydration_cost_est REAL,
            
            -- Telos
            priority TEXT,
            healing_policy TEXT,
            logs TEXT
        )''')
        conn.commit()
        conn.close()

    def add_task(self, task_data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO tasks VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )''', (
            task_data['id'],
            task_data['name'],
            task_data.get('type', 'GENERIC'),
            'PENDING',
            json.dumps(task_data.get('dependencies', [])),
            task_data.get('source', ''),
            task_data.get('schedule'),
            task_data.get('next_run_at', time.time()),
            task_data.get('energy_cost_est', 0.0),
            task_data.get('negentropy_value', 0.5),
            task_data.get('max_bid_price', 0.10),
            task_data.get('hydration_cost_est', 0.0),
            task_data.get('priority', 'NORMAL'),
            task_data.get('healing_policy', 'RETRY'),
            ''
        ))
        conn.commit()
        conn.close()

    def get_pending_tasks(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        now = time.time()
        c.execute("SELECT * FROM tasks WHERE status='PENDING' AND next_run_at <= ?", (now,))
        rows = c.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def update_status(self, task_id, status, logs=""):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE tasks SET status=?, logs=? WHERE id=?", (status, logs, task_id))
        conn.commit()
        conn.close()

    def get_task(self, task_id):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        conn.close()
        return dict(row) if row else None
