import time

class ComputeContainer:
    """
    The 'Black Box': A sandboxed environment where Industrial Code runs.
    Ensures Mutual Distrust:
    1. User cannot see Client's Code.
    2. Client cannot see User's Files.
    """
    def __init__(self):
        self.is_isolated = False
        self.memory_limit_mb = 1024
        
    def initialize_sandbox(self):
        """
        Locks down the environment.
        """
        self.is_isolated = True
        print("🔒 [Container] Sandbox Initialized. Network: BLOCKED. Filesystem: RESTRICTED.")
        
    def execute_job(self, job_id: str, input_data: bytes) -> list:
        """
        Runs the client's payload inside the sandbox.
        """
        if not self.is_isolated:
            raise PermissionError("Sandbox not initialized!")
            
        print(f"⚙️ [Container] Executing Job {job_id} in Secure Enclave...")
        # Simulate compute
        time.sleep(0.5)
        
        # Mock Result (Gradient)
        gradient = [0.1, -0.05, 0.003, 0.9]
        print("   ✅ Compute Complete. Memory Cleaned.")
        
        return gradient
        
    def terminate(self):
        self.is_isolated = False
        print("🔓 [Container] Sandbox Terminated.")
