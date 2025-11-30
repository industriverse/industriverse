from src.orchestration.task_db import TaskDB
import time

db = TaskDB()

# Capsule Task (Needs Hydration)
db.add_task({
    "id": "task_welding_sim",
    "name": "Welding Simulation V2",
    "type": "SIMULATION",
    "source": "capsule://industriverse-dac/welding-sim:v2.1",
    "priority": "NORMAL",
    "negentropy_value": 0.8,
    "max_bid_price": 0.15,
    "hydration_cost_est": 0.02
})

print("✅ Capsule Task Seeded.")
