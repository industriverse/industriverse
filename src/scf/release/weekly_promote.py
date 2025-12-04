import os
import shutil
import time
import json
import logging
from pathlib import Path

from src.scf.config import EXTERNAL_DRIVE, MODEL_ZOO, RELEASES

LOG = logging.getLogger("SCF.ReleaseManager")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def promote_latest():
    LOG.info("🚀 Starting Weekly Promotion Cycle...")
    
    if not MODEL_ZOO.exists():
        LOG.error("Model Zoo not found at %s", MODEL_ZOO)
        return

    # Pick latest checkpoint
    # In a real scenario, we would pick based on evaluation metrics in meta.json
    ckpts = sorted(MODEL_ZOO.glob("ckpt-*.pt"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not ckpts:
        LOG.warning("⚠️ No checkpoints found to release.")
        return

    latest = ckpts[0]
    LOG.info("   Selected Candidate: %s", latest.name)
    
    # Create Release Directory
    tag = time.strftime("week-%Y-%m-%d")
    outdir = RELEASES / tag
    outdir.mkdir(parents=True, exist_ok=True)
    
    # Copy Artifact
    dest = outdir / latest.name
    shutil.copy2(latest, dest)
    LOG.info("   Copied to: %s", dest)
    
    # Generate Metadata
    meta = {
        "released_at": time.time(),
        "tag": tag,
        "artifact": latest.name,
        "source_path": str(latest),
        "checksum": "sha256-placeholder"
    }
    
    (outdir / "meta.json").write_text(json.dumps(meta, indent=2))
    
    # Update "latest" symlink or pointer
    (RELEASES / "latest").write_text(tag)
    
    LOG.info("✅ Promotion Complete: %s", tag)

if __name__ == "__main__":
    promote_latest()
