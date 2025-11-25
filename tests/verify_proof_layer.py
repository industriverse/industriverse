import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from proof_layer.proof_schema import CapsuleProof, EnergySignature, PRINData, ProofEvidence
from proof_layer.utid import UTIDGenerator
from proof_layer.proof_registry import ProofRegistry
from proof_layer.zk_attestation import ZKAttestationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerifyProofLayer")

def test_proof_workflow():
    # 1. Initialize Components
    utid_gen = UTIDGenerator(host_secret="test_secret")
    registry = ProofRegistry(storage_path="data/test_proofs.jsonl")
    zk_service = ZKAttestationService()
    
    capsule_id = "capsule:rawmat:v1"
    
    # 2. Generate UTID
    utid = utid_gen.generate(capsule_id)
    logger.info(f"Generated UTID: {utid}")
    assert UTIDGenerator.verify_format(utid)
    
    # 3. Create Proof Object
    proof = CapsuleProof(
        proof_id=f"proof:{utid.split(':')[-1]}", # Simple ID for test
        capsule_id=capsule_id,
        utid=utid,
        energy_signature=EnergySignature(
            E_total_J=100.5,
            E_per_op_J=0.5,
            entropy_score=0.12
        ),
        prin=PRINData(
            value=0.85,
            components={"P_physics": 0.9, "P_coherence": 0.8, "P_novelty": 0.1},
            verdict="APPROVE"
        ),
        evidence=[
            ProofEvidence(type="energy_map_hash", value="sha256:mock")
        ],
        lineage={"parent_proofs": []}
    )
    
    # 4. Generate ZK Attestation
    attestation = zk_service.attest(proof.json())
    logger.info(f"ZK Attestation: {attestation}")
    proof.anchors.append(attestation)
    
    # 5. Register Proof
    proof_id = registry.register_proof(proof)
    logger.info(f"Registered Proof ID: {proof_id}")
    
    # 6. Retrieve and Verify
    retrieved = registry.get_proof(proof_id)
    assert retrieved is not None
    assert retrieved.utid == utid
    assert retrieved.prin.value == 0.85
    
    logger.info("Proof Layer Verification Successful!")

if __name__ == "__main__":
    test_proof_workflow()
