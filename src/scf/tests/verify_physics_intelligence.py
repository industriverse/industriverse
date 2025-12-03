import os
import shutil
import time
from src.datahub.ingestion.primordial_soup import PrimordialSoupIngestor
from src.scf.fertilization.fossil_validator import FossilValidator
from src.scf.fertilization.cfr_logger import CFRLogger
from src.security.emergency_stop import EmergencyStop
from scripts.operations.nightly_canary import NightlyCanary
import asyncio

def verify_primordial_soup():
    print("🧪 Verifying Primordial Soup Ingestion...")
    # Force mock mode by using a non-existent drive path
    ingestor = PrimordialSoupIngestor(source_drive="/non/existent/drive", output_dir="data/energy_atlas/test_fossils")
    ingestor.run_ingestion_cycle()
    
    fossils = os.listdir("data/energy_atlas/test_fossils")
    assert len(fossils) > 0, "No fossils created from Primordial Soup"
    print(f"✅ Ingested {len(fossils)} fossils.")
    
    # Cleanup
    shutil.rmtree("data/energy_atlas/test_fossils")

def verify_fossil_validation():
    print("🛡️ Verifying Fossil Validator...")
    validator = FossilValidator()
    
    # Case 1: Valid Fossil
    valid_packet = {
        "intent_id": "123",
        "context_slab_ref": "CTX",
        "negentropy_score": 0.5,
        "energy_trace_summary": {"joules_saved": 10.0},
        "proof_id": "PROOF_XYZ",
        "artifact_cid": "ipfs://QmHash",
        "verifier_result": "APPROVE"
    }
    is_valid, reason = validator.validate(valid_packet)
    assert is_valid, f"Valid fossil rejected: {reason}"
    print("✅ Valid fossil accepted.")
    
    # Case 2: Invalid Fossil (Zero Negentropy)
    invalid_packet = {
        "intent_id": "123",
        "context_slab_ref": "CTX",
        "negentropy_score": 0.0,
        "energy_trace_summary": {"joules_saved": 0.0},
        "proof_id": "PROOF_XYZ",
        "artifact_cid": "ipfs://QmHash",
        "verifier_result": "APPROVE"
    }
    is_valid, reason = validator.validate(invalid_packet)
    assert not is_valid, "Invalid fossil accepted (Zero Negentropy)"
    print("✅ Invalid fossil rejected (Zero Negentropy).")

def verify_cfr_integration():
    print("📜 Verifying CFR Logger Integration...")
    logger = CFRLogger()
    
    # Record a mock event
    intent = "Test Physics Intelligence"
    code = "print('Hello Physics')"
    review_result = {"verdict": "APPROVE", "score": 0.8}
    
    # This should trigger validation (internally mocked in record method for now)
    logger.record(intent, code, review_result)
    print("✅ CFR Logger recorded event.")

def verify_emergency_stop():
    print("🛑 Verifying Emergency Stop...")
    stop = EmergencyStop(control_file="data/datahub/test_control.json")
    
    # 1. Trigger
    stop.trigger("Test Reason", "Operator_Kunal")
    assert not stop.check_status(), "System should be STOPPED"
    print("✅ Emergency Stop Triggered.")
    
    # 2. Release (Fail - 1 sig)
    stop.release(["Operator_Kunal"])
    assert not stop.check_status(), "System should still be STOPPED (1 sig)"
    print("✅ Release rejected (insufficient signatures).")
    
    # 3. Release (Success - 2 sigs)
    stop.release(["Operator_Kunal", "Operator_Aletheia"])
    assert stop.check_status(), "System should be SAFE"
    print("✅ Emergency Stop Released.")
    
    # Cleanup
    if os.path.exists("data/datahub/test_control.json"):
        os.remove("data/datahub/test_control.json")

def verify_canary():
    print("🐤 Verifying Nightly Canary...")
    canary = NightlyCanary()
    asyncio.run(canary.run_suite())
    print("✅ Canary Suite executed.")

if __name__ == "__main__":
    verify_primordial_soup()
    verify_fossil_validation()
    verify_cfr_integration()
    verify_emergency_stop()
    verify_canary()
    print("\n🎉 ALL PHYSICS INTELLIGENCE CHECKS PASSED")
