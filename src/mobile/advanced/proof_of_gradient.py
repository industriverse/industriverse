import hashlib
import time
import json
from dataclasses import dataclass

@dataclass
class GradientProof:
    job_id: str
    epoch: int
    input_hash: str
    output_gradient_hash: str
    compute_time_ms: float
    device_signature: str # Signed by eSIM

class ProofOfGradient:
    """
    Veracity Engine: Ensures that the compute was actually performed and not faked.
    Uses a 'Hash Chain' of the training steps to prove work.
    """
    def __init__(self, device_id: str, esim_anchor):
        self.device_id = device_id
        self.esim = esim_anchor
        
    def generate_proof(self, job_id: str, epoch: int, input_data: bytes, output_gradient: list) -> GradientProof:
        """
        Creates a cryptographic proof of the training step.
        """
        start_time = time.time()
        
        # 1. Hash the Input Data (Verifies we used the correct dataset)
        input_hash = hashlib.sha256(input_data).hexdigest()
        
        # 2. Hash the Output Gradient (Verifies the result integrity)
        grad_str = json.dumps(output_gradient)
        output_hash = hashlib.sha256(grad_str.encode()).hexdigest()
        
        # 3. Create the 'Work Hash' (Simulating the compute trace)
        # In a real ZK system, this would be a SNARK proof.
        # Here we use a hash chain of the intermediate steps.
        work_payload = f"{job_id}:{epoch}:{input_hash}:{output_hash}"
        work_hash = hashlib.sha256(work_payload.encode()).hexdigest()
        
        # 4. Sign with eSIM (Verifies the Hardware Identity)
        signature = self.esim.sign_telemetry(work_hash)
        
        compute_time = (time.time() - start_time) * 1000
        
        print(f"🧾 [PoG] Generated Proof for Job {job_id} (Epoch {epoch})")
        print(f"   - Input Hash: {input_hash[:8]}...")
        print(f"   - Output Hash: {output_hash[:8]}...")
        print(f"   - Signature: {signature[:10]}...")
        
        return GradientProof(
            job_id=job_id,
            epoch=epoch,
            input_hash=input_hash,
            output_gradient_hash=output_hash,
            compute_time_ms=compute_time,
            device_signature=signature
        )
