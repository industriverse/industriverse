import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_grand_unification():
    print("🔍 Starting Grand Unification Verification...")

    headers = {
        "X-UTID": "UTID:REAL:BROWSER:DASHBOARD:20251124:nonce",
        "Content-Type": "application/json"
    }

    # 1. Trigger Thermal Sampling (Thermodynamics -> Proof)
    print("\n1. Triggering Thermal Sampling...")
    payload = {
        "problem_type": "combinatorial",
        "variables": {"x": [0, 1], "y": [0, 1]},
        "num_samples": 10,
        "temperature": 1.0
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/v1/thermodynamic/thermal/sample", json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            proof_hash = data.get("proof_hash")
            print(f"✅ Thermal Sampling Successful. Proof Hash: {proof_hash}")
        else:
            print(f"❌ Thermal Sampling Failed: {resp.text}")
            return
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # 2. Verify Proof Existence (Proof Economy)
    print("\n2. Verifying Proof in Repository...")
    # Give it a moment to propagate if async (though implementation looked sync)
    time.sleep(1) 
    try:
        resp = requests.get(f"{BASE_URL}/v1/proofs?limit=5", headers=headers)
        if resp.status_code == 200:
            proofs = resp.json()
            found = False
            for p in proofs:
                if p["proof_id"] == proof_hash:
                    found = True
                    print(f"✅ Proof {proof_hash} found in repository.")
                    print(f"   - Score: {p['metadata'].get('proof_score')}")
                    print(f"   - Energy: {p['metadata'].get('energy_joules')} J")
                    break
            if not found:
                print(f"❌ Proof {proof_hash} NOT found in recent proofs.")
        else:
            print(f"❌ Failed to fetch proofs: {resp.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

    # 3. Check Shield State (Real Entropy)
    print("\n3. Checking Shield State (Entropy)...")
    try:
        resp = requests.get(f"{BASE_URL}/v1/shield/state", headers=headers)
        if resp.status_code == 200:
            state = resp.json()
            metrics = state.get("metrics", {})
            entropy = metrics.get("system_entropy")
            print(f"✅ Shield State Retrieved.")
            print(f"   - System Entropy: {entropy}")
            print(f"   - Status: {state.get('status')}")
            if entropy > 0:
                print("   - Entropy is ACTIVE (Real Data).")
            else:
                print("   - Entropy is ZERO (Possibly Mock/Idle).")
        else:
            print(f"❌ Failed to fetch shield state: {resp.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

    # 4. Check Wallet (Identity)
    print("\n4. Checking User Wallet...")
    demo_utid = "UTID:USER:DEMO_001"
    try:
        resp = requests.get(f"{BASE_URL}/v1/utid/wallet/{demo_utid}", headers=headers)
        if resp.status_code == 200:
            wallet = resp.json()
            print(f"✅ Wallet Retrieved.")
            print(f"   - UTID: {wallet['utid']}")
            print(f"   - Credits: {wallet['credits']}")
            print(f"   - Trust Level: {wallet['trust_level']}")
        else:
            print(f"❌ Failed to fetch wallet: {resp.text}")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

    print("\n✨ Grand Unification Verification Complete.")

if __name__ == "__main__":
    test_grand_unification()
