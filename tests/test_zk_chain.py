import pytest
from src.zkp.roi_prover import ROIProver

def test_proof_generation():
    prover = ROIProver()
    report1 = {"week_id": "W1", "savings": 100}
    proof1 = prover.generate_proof(report1)
    
    assert proof1["previous_hash"] == "0" * 64
    assert len(proof1["current_hash"]) == 64
    
    report2 = {"week_id": "W2", "savings": 200}
    proof2 = prover.generate_proof(report2)
    
    assert proof2["previous_hash"] == proof1["current_hash"]

def test_proof_verification():
    prover = ROIProver()
    report = {"week_id": "W1", "savings": 100}
    proof = prover.generate_proof(report)
    
    assert prover.verify_proof(report, proof) == True
    
    # Tamper with report
    tampered_report = {"week_id": "W1", "savings": 999}
    assert prover.verify_proof(tampered_report, proof) == False
