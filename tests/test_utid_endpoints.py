from fastapi.testclient import TestClient

from src.bridge_api.server import app


client = TestClient(app)


def test_utid_generate_and_verify():
    gen_resp = client.post("/v1/utid/generate", json={"context": {"source": "test"}})
    assert gen_resp.status_code == 200
    utid = gen_resp.json()["utid"]
    parts = utid.split(":")
    assert parts[0:2] == ["UTID", "REAL"]
    assert len(parts) == 7  # includes attest signature
    assert parts[3].isdigit()

    verify_resp = client.post("/v1/utid/verify", json={"utid": utid})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["valid"] is True
