import pytest
from fastapi.testclient import TestClient
from src.bridge_api.server import app

client = TestClient(app)

def test_health_check():
    """Health check should pass without any headers."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_utid_middleware_invalid():
    """Request with invalid UTID should be blocked."""
    response = client.get("/adapters/mcp/status", headers={"X-UTID": "INVALID-123"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid UTID"}

def test_proof_middleware_injection():
    """Response should contain X-Proof-ID header."""
    response = client.get("/health")
    assert "X-Proof-ID" in response.headers
    assert len(response.headers["X-Proof-ID"]) > 0

def test_ai_shield_blocking():
    """Request with 'unsafe' in URL should be blocked by AI Shield."""
    response = client.get("/health?query=unsafe_command")
    assert response.status_code == 400
    assert "AI Shield" in response.json()["detail"]

def test_proof_generation_endpoint():
    """Proof generation endpoint should work."""
    payload = {
        "title": "Test Proof",
        "requester": {"org": "test"},
        "artifacts": [],
        "proof_types": ["basic"]
    }
    response = client.post("/v1/proofs/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "proof_id" in data
    assert data["status"] == "queued"

if __name__ == "__main__":
    # Manual run if pytest not installed
    try:
        test_health_check()
        print("✅ Health Check Passed")
        test_utid_middleware_invalid()
        print("✅ UTID Invalid Check Passed")
        test_proof_middleware_injection()
        print("✅ Proof Injection Passed")
        test_ai_shield_blocking()
        print("✅ AI Shield Blocking Passed")
        test_proof_generation_endpoint()
        print("✅ Proof Generation Passed")
    except AssertionError as e:
        print(f"❌ Test Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
