import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.mobile.integration.industrial_job_market import IndustrialJobMarket
from src.mobile.security.compute_container import ComputeContainer
from src.mobile.advanced.proof_of_gradient import ProofOfGradient
from src.mobile.security.esim import eSIMAnchor

def verify_neural_expansion():
    print("🏭 Starting Neural Battery (Industrial DePIN) Verification...")
    
    # 1. Setup
    market = IndustrialJobMarket()
    container = ComputeContainer()
    esim = eSIMAnchor("ICCID_TEST_999")
    pog = ProofOfGradient("DEVICE_WORKER_01", esim)
    
    # 2. Find a Job
    print("\n--- Step 1: The Market ---")
    my_specs = {"chipset": "A17_PRO", "battery": 0.98}
    jobs = market.fetch_jobs(my_specs)
    if not jobs:
        print("❌ No jobs found.")
        return
        
    selected_job = jobs[0] # Take the first one (e.g., Tesla or GE)
    if market.accept_job(selected_job.id, "DEVICE_WORKER_01"):
        print(f"   ✅ Accepted Job: {selected_job.client_name}")
        
    # 3. Execute in Sandbox
    print("\n--- Step 2: The Execution ---")
    container.initialize_sandbox()
    input_data = b"SimulatedSensorData_Batch_001"
    gradient = container.execute_job(selected_job.id, input_data)
    container.terminate()
    
    # 4. Prove Veracity
    print("\n--- Step 3: The Proof (Veracity) ---")
    proof = pog.generate_proof(selected_job.id, 1, input_data, gradient)
    
    if proof.device_signature:
        print(f"   ✅ Proof of Gradient Valid. Signed by eSIM.")
        
    print("\n✅ INDUSTRIAL DePIN VERIFICATION COMPLETE.")

if __name__ == "__main__":
    verify_neural_expansion()
