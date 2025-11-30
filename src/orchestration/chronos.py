import time
import json
from src.orchestration.task_db import TaskDB
from src.orchestration.kairos import KairosOptimizer
from src.orchestration.hydrator import ServiceHydrator
from src.orchestration.capsule_resolver import CapsuleResolver

class Chronos:
    """
    The Timekeeper. Manages the Dependency Graph and Scheduling Loop.
    """
    def __init__(self, db_path="data/orchestration/tasks.db"):
        self.db = TaskDB(db_path)
        self.kairos = KairosOptimizer()
        self.hydrator = ServiceHydrator()
        self.resolver = CapsuleResolver()
        self.running = False

    def check_dependencies(self, task):
        """Returns True if all dependencies are COMPLETED."""
        deps = json.loads(task['dependencies'])
        if not deps:
            return True
        
        for dep_id in deps:
            dep_task = self.db.get_task(dep_id)
            if not dep_task or dep_task['status'] != 'COMPLETED':
                return False
        return True

    def tick(self):
        """Single tick of the scheduler loop."""
        pending = self.db.get_pending_tasks()
        print(f"[Chronos] Found {len(pending)} pending tasks.")

        for task in pending:
            # 1. Check Dependencies (DAG)
            if self.check_dependencies(task):
                # 2. Hand off to Kairos (Economics)
                decision = self.kairos.evaluate(task)
                
                if decision == "EXECUTE":
                    print(f"[Chronos] >>> Dispatching: {task['name']}")
                    
                    # Hydration Step
                    source = task.get('source')
                    if source and source.startswith("capsule://"):
                        b2_path = self.resolver.resolve(source)
                        if b2_path:
                            local_path = self.hydrator.hydrate(b2_path)
                            print(f"[Chronos] Service Ready at: {local_path}")
                        else:
                            print(f"[Chronos] ❌ Failed to resolve capsule: {source}")
                            self.db.update_status(task['id'], "FAILED", "Capsule Resolution Failed")
                            continue

                    # In a real system, this would push to an Executor Queue.
                    # For MVP, we mark as RUNNING.
                    self.db.update_status(task['id'], "RUNNING")
                    # Simulate Execution (Placeholder for Executor)
                    self.simulate_execution(task)
                else:
                    print(f"[Chronos] Deferring {task['name']} (Kairos Decision: {decision})")
            else:
                print(f"[Chronos] Waiting on dependencies for {task['name']}")

    def simulate_execution(self, task):
        """Mock execution for MVP."""
        time.sleep(0.5)
        print(f"[Executor] Finished {task['name']}")
        self.db.update_status(task['id'], "COMPLETED", "Success")

    def run(self):
        self.running = True
        print("⏳ Chronos Timekeeper Started.")
        while self.running:
            self.tick()
            time.sleep(5)

if __name__ == "__main__":
    c = Chronos()
    c.run()
