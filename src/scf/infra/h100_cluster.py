import os
import subprocess
import time
from typing import Dict, Any

class H100Cluster:
    """
    Manages the remote H100 training environment.
    Handles GPU monitoring, environment setup, and job execution.
    """
    def __init__(self):
        self.gpu_info = self._get_gpu_info()
        print(f"🖥️  Cluster Manager Online.")
        print(f"   GPU Detected: {self.gpu_info.get('name', 'Unknown')}")
        print(f"   VRAM: {self.gpu_info.get('memory_total', 'Unknown')}")

    def _get_gpu_info(self) -> Dict[str, str]:
        """
        Queries nvidia-smi for GPU details.
        """
        try:
            # Simple check using nvidia-smi
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                name, memory = result.stdout.strip().split(',')
                return {"name": name.strip(), "memory_total": memory.strip()}
        except FileNotFoundError:
            pass
        
        return {"name": "CPU Mode (No GPU)", "memory_total": "N/A"}

    def setup_environment(self):
        """
        Configures high-performance settings for the H100.
        """
        # Set PyTorch CUDA allocator config for efficiency
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:512'
        print("   ⚙️  Environment Configured for High-Performance Compute.")

    def run_job(self, script_path: str, args: list = []):
        """
        Executes a training job on the cluster.
        """
        print(f"   🚀 Launching Job: {script_path}")
        start_time = time.time()
        
        cmd = ['python3', script_path] + args
        try:
            subprocess.run(cmd, check=True)
            duration = time.time() - start_time
            print(f"   ✅ Job Complete. Duration: {duration:.2f}s")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Job Failed with error: {e}")

if __name__ == "__main__":
    cluster = H100Cluster()
    cluster.setup_environment()
