from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class ComputeJob:
    id: str
    client_name: str # e.g., "General Electric"
    task_type: str   # "TRAINING", "INFERENCE", "SIMULATION"
    reward_credits: float
    min_chipset: str # e.g., "A17_PRO", "SNAPDRAGON_8GEN3"
    required_battery: float # e.g., 0.90

class IndustrialJobMarket:
    """
    The Industrial Compute Exchange (ICE): Matches Industrial Clients with Mobile Devices.
    """
    def __init__(self):
        self.open_jobs: List[ComputeJob] = [
            ComputeJob("JOB_GE_001", "General Electric", "TRAINING", 50.0, "A16_BIONIC", 0.85),
            ComputeJob("JOB_TSLA_99", "Tesla Motors", "SIMULATION", 100.0, "A17_PRO", 0.95),
            ComputeJob("JOB_NASA_X", "NASA JPL", "INFERENCE", 75.0, "ANY", 0.80)
        ]
        
    def fetch_jobs(self, device_specs: dict) -> List[ComputeJob]:
        """
        Returns jobs that match the device's capabilities.
        """
        eligible_jobs = []
        print(f"🏭 [Market] Fetching jobs for device: {device_specs['chipset']}")
        
        for job in self.open_jobs:
            # Simple mock matching logic
            if job.min_chipset == "ANY" or job.min_chipset == device_specs['chipset']:
                eligible_jobs.append(job)
                
        return eligible_jobs
        
    def accept_job(self, job_id: str, device_id: str) -> bool:
        """
        Locks the job for this device.
        """
        job = next((j for j in self.open_jobs if j.id == job_id), None)
        if job:
            print(f"🤝 [Market] Contract Signed: {device_id} accepts {job.id} from {job.client_name}")
            print(f"   💰 Reward: {job.reward_credits} Credits")
            return True
        return False
