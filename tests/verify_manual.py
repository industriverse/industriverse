import subprocess
import time
import urllib.request
import urllib.error
import json
import sys
import os
import signal

SERVER_PORT = 8001
BASE_URL = f"http://localhost:{SERVER_PORT}"

def start_server():
    print(f"🚀 Starting server on port {SERVER_PORT}...")
    # Run uvicorn as a subprocess
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.bridge_api.server:app", "--host", "127.0.0.1", "--port", str(SERVER_PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # Wait for server to start
    for i in range(10):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/health") as response:
                if response.status == 200:
                    print("✅ Server is up!")
                    return process
        except:
            time.sleep(1)
    
    print("❌ Server failed to start.")
    process.kill()
    sys.exit(1)

def stop_server(process):
    print("🛑 Stopping server...")
    process.terminate()
    process.wait()

def run_test(name, func):
    try:
        func()
        print(f"✅ {name} Passed")
    except Exception as e:
        print(f"❌ {name} Failed: {e}")
        # raise e # Uncomment to stop on first failure

def test_health():
    with urllib.request.urlopen(f"{BASE_URL}/health") as response:
        data = json.load(response)
        assert data["status"] == "healthy"

def test_utid_invalid():
    req = urllib.request.Request(f"{BASE_URL}/adapters/mcp/status")
    req.add_header("X-UTID", "INVALID-123")
    try:
        urllib.request.urlopen(req)
        raise AssertionError("Should have failed with 403")
    except urllib.error.HTTPError as e:
        assert e.code == 403
        data = json.load(e)
        assert data["detail"] == "Invalid UTID"

def test_proof_injection():
    with urllib.request.urlopen(f"{BASE_URL}/health") as response:
        headers = dict(response.getheaders())
        assert "x-proof-id" in headers or "X-Proof-ID" in headers
        proof_id = headers.get("x-proof-id") or headers.get("X-Proof-ID")
        assert len(proof_id) > 0

def test_ai_shield_blocking():
    try:
        urllib.request.urlopen(f"{BASE_URL}/health?query=unsafe_command")
        raise AssertionError("Should have failed with 400")
    except urllib.error.HTTPError as e:
        assert e.code == 400
        data = json.load(e)
        assert "AI Shield" in data["detail"]

def test_proof_generation():
    payload = {
        "title": "Test Proof",
        "requester": {"org": "test"},
        "artifacts": [],
        "proof_types": ["basic"]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/v1/proofs/generate", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req) as response:
        assert response.status == 200
        resp_data = json.load(response)
        assert "proof_id" in resp_data
        assert resp_data["status"] == "queued"

if __name__ == "__main__":
    server_proc = start_server()
    try:
        run_test("Health Check", test_health)
        run_test("UTID Invalid", test_utid_invalid)
        run_test("Proof Injection", test_proof_injection)
        run_test("AI Shield Blocking", test_ai_shield_blocking)
        run_test("Proof Generation", test_proof_generation)
    finally:
        stop_server(server_proc)
