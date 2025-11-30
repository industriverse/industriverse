class TelosSupervisor:
    """
    The Supervisor. Handles Alignment and Self-Healing.
    """
    def __init__(self, db):
        self.db = db

    def handle_failure(self, task, error_log):
        """
        Called when a task fails. Decides whether to Retry, Fix, or Abort.
        """
        print(f"[Telos] 🚨 Analyzing failure for {task['name']}...")
        
        policy = task['healing_policy']
        
        if policy == 'ABORT':
            print("[Telos] Policy is ABORT. Marking FAILED.")
            self.db.update_status(task['id'], "FAILED", error_log)
            return

        # Simulate "Trifecta" Diagnosis
        diagnosis = self.diagnose_error(error_log)
        print(f"[Telos] Diagnosis: {diagnosis}")

        if diagnosis == "TRANSIENT_ERROR":
            print("[Telos] Applying Fix: RETRY immediately.")
            self.db.update_status(task['id'], "PENDING", "Telos: Retrying after transient error.")
        
        elif diagnosis == "CONFIG_ERROR":
            print("[Telos] Applying Fix: Patching Config and Retrying.")
            # In prod, this would actually edit the config file.
            self.db.update_status(task['id'], "PENDING", "Telos: Config patched.")
            
        else:
            print("[Telos] Unknown Error. Escalating to Human.")
            self.db.update_status(task['id'], "FAILED", "Telos: Escalated.")

    def diagnose_error(self, log):
        """Mock LLM Diagnosis."""
        if "ConnectionRefused" in log:
            return "TRANSIENT_ERROR"
        elif "KeyError" in log:
            return "CONFIG_ERROR"
        return "UNKNOWN"
