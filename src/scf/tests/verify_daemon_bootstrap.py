import os
import shutil
import time
import json
import asyncio
from pathlib import Path
from src.scf.daemon.scf_daemon import SCFSovereignDaemon, EXTERNAL_DRIVE, FOSSIL_VAULT, MODEL_ZOO

def setup_mock_environment():
    print("🛠 Setting up Mock Environment...")
    # Override paths for testing if needed, but scf_daemon uses env var or default.
    # We will use the paths defined in scf_daemon (which default to /Volumes/TOSHIBA EXT... or env)
    # For this test, let's force a local temp dir to avoid messing with real drive if it exists
    
    TEST_ROOT = Path("data/daemon_test_env")
    if TEST_ROOT.exists():
        shutil.rmtree(TEST_ROOT)
    TEST_ROOT.mkdir(parents=True)
    
    os.environ["EXTERNAL_DRIVE"] = str(TEST_ROOT.absolute())
    
    # Re-import to pick up env var change? 
    # Python imports are cached, so we need to patch the module variables or reload.
    # Easier to just set the variables on the imported module instances if possible, 
    # or rely on the fact that we will run this script in a separate process or just use the class.
    
    # Actually, let's just create the dirs where the daemon expects them if we can't change it easily.
    # But wait, scf_daemon reads env var at module level.
    # So we should have set env var BEFORE importing. 
    # Since we already imported, let's monkeypatch.
    import src.scf.daemon.scf_daemon as d
    import src.scf.daemon.gpu_worker as w
    import src.scf.fertilization.fossil_batcher as b
    
    d.EXTERNAL_DRIVE = TEST_ROOT
    d.FOSSIL_VAULT = TEST_ROOT / "fossil_vault"
    d.MODEL_ZOO = TEST_ROOT / "model_zoo"
    d.RELEASES = TEST_ROOT / "release_history"
    d.ZK_PROOFS = TEST_ROOT / "zk_proofs"
    d.CONTROL_FILE = TEST_ROOT / "data/scf/control.json"
    
    w.EXTERNAL_DRIVE = TEST_ROOT
    w.MODEL_ZOO = TEST_ROOT / "model_zoo"
    
    b.EXTERNAL_DRIVE = TEST_ROOT
    b.FOSSIL_VAULT = TEST_ROOT / "fossil_vault"

    # Create Dirs
    for p in [d.FOSSIL_VAULT, d.MODEL_ZOO, d.RELEASES, d.ZK_PROOFS, d.CONTROL_FILE.parent]:
        p.mkdir(parents=True, exist_ok=True)
        
    # Create Mock Fossil
    mock_fossil = d.FOSSIL_VAULT / "fossil-test-001.json"
    mock_data = [{"energy": 100, "entropy": 0.5, "embedding": [0.1]*128} for _ in range(10)]
    mock_fossil.write_text(json.dumps(mock_data))
    
    print(f"   Created mock fossil at {mock_fossil}")
    return d

async def run_test():
    d = setup_mock_environment()
    
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    root.addHandler(handler)
    
    print("🚀 Starting Daemon Test...")
    print(f"   Daemon Module MODEL_ZOO: {d.MODEL_ZOO}")
    daemon = d.SCFSovereignDaemon()
    
    # Run loop for a few seconds
    task = asyncio.create_task(daemon.start())
    
    print("   Daemon running... waiting for processing...")
    await asyncio.sleep(30) # Give it time to pick up fossil and run worker
    
    if task.done():
        print("⚠️ Daemon task finished early!")
        try:
            exc = task.exception()
            if exc:
                print(f"❌ Daemon crashed with: {exc}")
                import traceback
                traceback.print_exception(type(exc), exc, exc.__traceback__)
        except Exception as e:
            print(f"   Could not retrieve exception: {e}")
    
    # Check for results
    processed_files = list((d.FOSSIL_VAULT / "processed").glob("*"))
    checkpoints = list(d.MODEL_ZOO.glob("*.pt"))
    proofs = list(d.ZK_PROOFS.glob("*.json"))
    
    print(f"   Processed Fossils: {[f.name for f in processed_files]}")
    print(f"   Checkpoints: {[f.name for f in checkpoints]}")
    print(f"   ZK Proofs: {[f.name for f in proofs]}")
    print(f"   Vault Contents: {[f.name for f in d.FOSSIL_VAULT.glob('*')]}")
    
    # Print logs
    log_dir = d.EXTERNAL_DRIVE / "logs"
    if log_dir.exists():
        for log_file in log_dir.glob("*.log"):
            print(f"   --- Log: {log_file.name} ---")
            print(log_file.read_text())
            print("   ---------------------------")
    
    assert len(processed_files) > 0, "Fossil was not archived!"
    assert len(checkpoints) > 0, "Checkpoint was not created!"
    assert len(proofs) > 0, "ZK Proof was not minted!"
    
    print("🛑 Stopping Daemon...")
    daemon.master.running = False
    await task
    print("✅ Test Passed!")

if __name__ == "__main__":
    asyncio.run(run_test())
