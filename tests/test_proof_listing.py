from fastapi.testclient import TestClient

from src.bridge_api.server import app


client = TestClient(app)


def test_proof_generate_and_list_with_energy_filter():
    # Obtain a valid UTID
    utid_resp = client.post("/v1/utid/generate", json={"context": {"source": "test-proof"}})
    assert utid_resp.status_code == 200
    utid = utid_resp.json()["utid"]

    # Generate a proof with UTID and energy metadata
    payload = {
        "title": "test",
        "requester": {"id": "tester"},
        "artifacts": [],
        "proof_types": ["unit"],
        "anchor": {"utid": utid},
        "metadata": {"energy_joules": 42.5},
    }
    gen_resp = client.post("/v1/proofs/generate", json=payload, headers={"X-UTID": utid})
    assert gen_resp.status_code == 200
    proof_id = gen_resp.json()["proof_id"]
    assert proof_id

    list_resp = client.get("/v1/proofs", params={"min_energy": 40, "max_energy": 50}, headers={"X-UTID": utid})
    assert list_resp.status_code == 200
    proofs = list_resp.json()
    assert any(p["proof_id"] == proof_id for p in proofs)

    # Verify proof status transition
    verify_resp = client.post("/v1/proofs/verify", json={"proof_hash": gen_resp.json()["proof_hash"], "verifier": "tester"}, headers={"X-UTID": utid})
    assert verify_resp.status_code == 200
    anchors = verify_resp.json().get("anchors", [])
    assert anchors
    # Update status explicitly
    status_resp = client.post(f"/v1/proofs/{proof_id}/status", json={"status": "validated", "anchors": anchors}, headers={"X-UTID": utid})
    assert status_resp.status_code == 200
