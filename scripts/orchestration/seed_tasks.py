from src.orchestration.task_db import TaskDB
import time

db = TaskDB()

# 1. Ingest Task (Low Value, High Priority)
db.add_task({
    "id": "task_ingest",
    "name": "Ingest Sensor Data",
    "type": "INGEST",
    "priority": "CRITICAL", # Should run regardless of price
    "negentropy_value": 0.1,
    "max_bid_price": 0.05
})

# 2. Simulation Task (High Value, High Cost, Dependent on Ingest)
db.add_task({
    "id": "task_sim",
    "name": "Fusion Simulation",
    "type": "SIMULATION",
    "dependencies": ["task_ingest"],
    "priority": "NORMAL",
    "negentropy_value": 0.9, # High Value
    "max_bid_price": 0.20    # Willing to pay more
})

# 3. Audit Task (Low Value, Low Cost, Dependent on Sim)
db.add_task({
    "id": "task_audit",
    "name": "Generate Audit PDF",
    "type": "REPORT",
    "dependencies": ["task_sim"],
    "priority": "NORMAL",
    "negentropy_value": 0.2,
    "max_bid_price": 0.08    # Cheapskate
})

print("✅ Tasks Seeded.")
