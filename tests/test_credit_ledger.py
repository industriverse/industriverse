from src.protocol_layer.protocols.credit_ledger import CreditLedger, compute_utid


def test_merkle_root_and_proof():
    ledger = CreditLedger()
    roots = []
    for i in range(3):
        utid = compute_utid(f"hash{i}", None, f"root{i}")
        ledger.append_execution(utid=utid, uri=f"capsule://x/{i}", telemetry={"execution_cost": 1.0, "credit_root": f"root{i}"})
        roots.append(utid)

    root = ledger.merkle_root()
    assert root
    proof_root, proof_path = ledger.merkle_proof(roots[1])
    assert proof_root == root
    assert proof_path, "proof path should not be empty"


def test_verify_proof_roundtrip():
    ledger = CreditLedger()
    utids = []
    for i in range(4):
        utid = compute_utid(f"h{i}", None, f"r{i}")
        utids.append(utid)
        ledger.append_execution(utid=utid, uri=f"capsule://x/{i}", telemetry={"execution_cost": 1.0, "credit_root": f"r{i}"})
    root, proof = ledger.merkle_proof(utids[2])
    assert ledger.verify_proof(utids[2], root, proof)
